#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: 
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2022, NextGIS <info@nextgis.com>

import argparse
import gdal, ogr
import os
import shutil

'''
test run

docker run -it -v ${PWD}:/data ods2qml:1.0  /bin/bash

python3 run.py sample-features.gpkg sample-boundaries

'''

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Crop of polygon layer by features of second polygon layer.',
            formatter_class=PrettyFormatter)

    parser.add_argument('file1', type=str,help='Source file')
    parser.add_argument('regionsdir', type=str,help='folder with regions layers, one region in file, any vector format')


    parser.epilog = \
        '''Samples:
%(prog)s sample-features.gpkg sample-boundaries

''' \
        % {'prog': parser.prog}
    return parser

parser = argparser_prepare()
args = parser.parse_args()

file1 = args.file1
regionsdir = args.regionsdir

assert os.path.isfile(file1)

assert os.path.isdir(regionsdir)
regions_layers=list()
for dirpath, dnames, fnames in os.walk(regionsdir):
    for f in fnames:
        #if f.lower().endswith("gpkg"):
        if 'approx' not in f and 'parts' not in 'f' and f.lower().endswith("geojson"):
            filename = os.path.join(dirpath, f)
            
            #test if this ogr compatible
            format_ok = False
            ds_test = None
            try:
                ds_test = gdal.OpenEx(filename,gdal.OF_READONLY+gdal.OF_VECTOR)
                if ds_test is not None: 
                    ds_test = True
                else:
                    print(filename+' is not valid file for gdal, skipped')
            except BaseException as err:
                ds_test = False
                print(filename+' is not valid file for gdal, skipped')
            if ds_test is not None:
                regions_layers.append(os.path.join(dirpath, f))
                del ds_test
            
assert(len(regions_layers)>0)
total=len(regions_layers)

regions_layers.sort()

exportdir = os.path.join(os.path.dirname(file1),'intersection')
if not os.path.exists(exportdir): os.makedirs(exportdir)

#features    
ds1 = gdal.OpenEx(file1,gdal.OF_READONLY)
assert ds1 is not None
layer1 = ds1.GetLayer()
assert layer1 is not None
assert layer1.GetFeatureCount() > 0

cnt=0
for boundary_filename in regions_layers:
    cnt=cnt+1
    cont = True
    print('{cnt}/{total} {name}'.format(cnt=cnt,total=total,name=os.path.splitext(os.path.basename(boundary_filename))[0]))
    
    dst_prefix = os.path.splitext(os.path.basename(boundary_filename))[0]
    out_filename = os.path.join(exportdir,dst_prefix+'.gpkg')
    if os.path.exists(out_filename):
        print('extract skipped, result file already exists')
        cont = False

    if cont == True:
        ds2 = gdal.OpenEx(boundary_filename,gdal.OF_READONLY)
        assert ds2 is not None
        layer2 = ds2.GetLayer()
        assert layer2 is not None
        assert layer2.GetFeatureCount() > 0

        feature = layer2.GetNextFeature()
        
        v1=layer1.GetFeatureCount()
        layer1.SetSpatialFilter(feature.GetGeometryRef())
        v2=layer1.GetFeatureCount()
        if v2 == 0:
            print('extract skipped, no features found')
            continue

        opt = []
        drv = ogr.GetDriverByName('GPKG')
        out_ds = drv.CreateDataSource(out_filename, options=opt)
        
        layer_out = out_ds.CopyLayer(layer1, 'intersection', 
            options=[
            ]
        )

