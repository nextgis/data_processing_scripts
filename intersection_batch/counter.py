#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Project:
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2022-2023, NextGIS <info@nextgis.com>

import argparse
import glob
from osgeo import gdal, ogr
import os
import time

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Calculate count of buildings in each region. Create csv file', formatter_class=PrettyFormatter)

    parser.add_argument('file1', type=str, help='building layer')
    parser.add_argument('regionsdir', type=str, help='folder with geojson boundaries')


    parser.epilog = \
        '''
        Samples:
%(prog)s sample-features.gpkg sample-boundaries

Script use approx.geojson files if they exist for speed optimitation

''' \
        % {'prog': parser.prog}
    return parser

def approx_file_has_manyfeatures(filename):
    fn2 = filename.replace('.geojson', '.approx.geojson')
    if os.path.isfile(fn2):
        approx_features = get_feature_count(fn2)
        if approx_features > 1:
            return True
    return False

def get_feature_count(filename):
    ds1 = gdal.OpenEx(file1, gdal.OF_READONLY)
    assert ds1 is not None
    layer1 = ds1.GetLayer()
    assert layer1 is not None
    c = layer1.GetFeatureCount()
    del layer1
    del ds1
    return c

def geom2geojsonfile(geom,path):
    outDriver = ogr.GetDriverByName('GeoJSON')

    # Create the output GeoJSON
    if os.path.isfile(path):
        os.unlink(path)
    print('geometry dumped to '+os.path.abspath(path))
    outDataSource = outDriver.CreateDataSource(path)
    outLayer = outDataSource.CreateLayer(path, geom_type=ogr.wkbPoint )

    # Get the output Layer's Feature Definition
    featureDefn = outLayer.GetLayerDefn()

    # create a new feature
    outFeature = ogr.Feature(featureDefn)

    # Set new geometry
    outFeature.SetGeometry(geom)

    # Add new feature to output Layer
    outLayer.CreateFeature(outFeature)

    # dereference the feature
    outFeature = None

    # Save and close DataSources
    outDataSource = None

def process_region(boundary_filename=None, clip_straight=True, feature_num=0, boundary_geometry=None):
    start_unixtime = time.time()
    
    if boundary_filename is not None:
        ds2 = gdal.OpenEx(boundary_filename, gdal.OF_READONLY)
        assert ds2 is not None
        layer2 = ds2.GetLayer()
        assert layer2 is not None
        assert layer2.GetFeatureCount() > 0
        feature = layer2.GetNextFeature()
        boundary_geometry = feature.GetGeometryRef()
    else:
        #used for countries with sparce areas like USA
        assert boundary_geometry is not None
        
    if clip_straight:
        # spatial filter by boundary
        layer1.SetSpatialFilter(boundary_geometry)
    else:
        # quick spatial filter by envelope, then by boundary. This turned out to be not needed. Not used.
        envelope_tuple = boundary_geometry.GetEnvelope()
        layer1.SetSpatialFilterRect(
            envelope_tuple[0], envelope_tuple[2], envelope_tuple[1], envelope_tuple[3])
        #not implemented


    feature_count = layer1.GetFeatureCount()

    process_time = int(time.time()-start_unixtime)
    return feature_count, process_time


parser = argparser_prepare()
args = parser.parse_args()

clip_straight = True

file1 = args.file1
regionsdir = args.regionsdir
csv_path = 'count.csv'

assert os.path.isfile(file1)
gdal.UseExceptions()

'''
if file approx present and has several features:
calculate count in each feature, then plus

Оптимизация для стран типа США
В слое границ 1 фича.
В слое approx несколько фич
'''

assert os.path.isdir(regionsdir)
regions_layers = list()
print('Check input geojson files for validity')
for f in glob.glob(regionsdir+'/*.geojson'):
    if 'approx' not in f and 'parts' not in f and 'sample' not in f and f.lower().endswith("geojson"):
        filename = f

        # test if this ogr compatible
        format_ok = False
        ds_test = None
        try:
            ds_test = gdal.OpenEx(filename, gdal.OF_READONLY+gdal.OF_VECTOR)
            if ds_test is not None:
                ds_test = True
            else:
                print(filename+' is not valid file for gdal, skipped')
        except BaseException as err:
            ds_test = False
            print(filename+' is not valid file for gdal, skipped')
        if ds_test is not None:
            regions_layers.append(f)
            del ds_test

assert (len(regions_layers) > 0)
total = len(regions_layers)
regions_layers.sort()

exportdir = regionsdir  # os.path.join(os.path.dirname(file1),'intersection')

# features
print('Check input database is valid and not empty')
ds1 = gdal.OpenEx(file1, gdal.OF_READONLY)
assert ds1 is not None
layer1 = ds1.GetLayer()
assert layer1 is not None
total_feature_count = layer1.GetFeatureCount()
assert total_feature_count > 0
print('Number of features in the input database: ' + str(total_feature_count))

# print csv header
with open(csv_path, "w") as text_file:
    text_file.write('''REGION;NUM;TIME'''+"\n")
    print('REGION;NUM;TIME')

cnt = 0
for boundary_filename in regions_layers:
    cnt = cnt + 1

    name = os.path.splitext(os.path.basename(boundary_filename))[0]
    # print('{cnt}/{total} {name}'.format(cnt=cnt,total=total,name=name))

    if approx_file_has_manyfeatures(boundary_filename):
        approx_features = get_feature_count(boundary_filename)
        # clip country boundary by approx boyndary
        # return just Kaliningrad oblast, just Alaska, just USA ocean island
        ds_approx = gdal.OpenEx(boundary_filename.replace(
            '.geojson', '.approx.geojson'), gdal.OF_READONLY)
        assert ds_approx is not None
        approx_layer = ds_approx.GetLayer()

        ds_boundary = gdal.OpenEx(boundary_filename, gdal.OF_READONLY)
        assert ds_boundary is not None
        real_boundary_layer = ds_boundary.GetLayer()
        real_boundary_feature = real_boundary_layer.GetNextFeature()
        country_feature_count = 0
        country_time = 0
        for approx_feature in approx_layer:
            approx_geom = approx_feature.GetGeometryRef()
            real_boundary_geom = real_boundary_feature.GetGeometryRef()
            if not real_boundary_geom.IsValid():
                real_boundary_geom = real_boundary_geom.Buffer(0)

            boundary_part_geom = real_boundary_geom.Intersection(
                approx_geom)
            if boundary_part_geom is None:
                print('boundary_part_geom is none')
                geom2geojsonfile(real_boundary_geom,'debug.real_boundary_geom.geojson')
                geom2geojsonfile(approx_geom,'debug.approx_geom.geojson')
                quit('stoped, invalid geometry')
            assert boundary_part_geom is not None,real_boundary_geom.ExportToJson()+' ' +approx_geom.ExportToJson()

            feature_count, process_time = process_region(
                boundary_filename=None, clip_straight=True, boundary_geometry=boundary_part_geom.Clone())
            country_feature_count = country_feature_count+feature_count
            country_time = country_time+process_time

        del approx_layer
        del ds_approx
        del real_boundary_feature
        del real_boundary_layer
        del ds_boundary
        feature_count = country_feature_count
        process_time = country_time
    else:
        feature_count, process_time = process_region(
            boundary_filename, clip_straight=True)

    csv_string = '{name};{feature_count};{process_time}'.format(
        name=name, feature_count=feature_count, process_time=process_time)
    print(csv_string)
    with open(csv_path, "a") as text_file:
        text_file.write(csv_string+"\n")
