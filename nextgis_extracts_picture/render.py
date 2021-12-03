#!/usr/bin/python3
# -*- coding: utf8 -*-

import os
import shutil
import argparse
import zipfile
import random
import string
from osgeo import gdal, ogr

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Export QGIS map composer layout to png using pyqgis',
            formatter_class=PrettyFormatter)
    parser.add_argument('extract',   help='Path to extract zip archive')
    parser.add_argument('prefix',   help='Prefix for output images filename')


    return parser


def main():
    parser = argparser_prepare()
    args = parser.parse_args()
    
    #unpack extract
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    unpack_dir = os.path.join('/data','extract_' + random_string)
    if os.path.exists(unpack_dir):
        shutil.rmtree(unpack_dir)
    os.makedirs(unpack_dir)
    with zipfile.ZipFile('/data/'+args.extract, 'r') as zip_ref:
        zip_ref.extractall(unpack_dir)
        
    #-----------------------------
    #get bbox for land.shp
    source_layer_path = os.path.join(unpack_dir,'data','land.shp')
    assert os.path.isfile(source_layer_path),'not found file for bbox generation '+source_layer_path
    
    ds = gdal.OpenEx(source_layer_path,gdal.OF_READONLY)
    assert ds is not None
    layer = ds.GetLayer()
    assert layer is not None
    extent = layer.GetExtent()
    
    # Create a Polygon from the extent tuple
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(extent[0],extent[2])
    ring.AddPoint(extent[1], extent[2])
    ring.AddPoint(extent[1], extent[3])
    ring.AddPoint(extent[0], extent[3])
    ring.AddPoint(extent[0],extent[2])
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    
    # Save poly extent to a new layer
    extent_filename = os.path.join(unpack_dir,'extent_region.geojson')
    extent_driver = ogr.GetDriverByName("GeoJSON")

    if os.path.exists(extent_filename):
        extent_driver.DeleteDataSource(extent_filename)
    extent_ds = extent_driver.CreateDataSource(extent_filename)
    extent_layer = extent_ds.CreateLayer("extent_region", geom_type=ogr.wkbPolygon)
    extent_layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
    feature_defn = extent_layer.GetLayerDefn()
    feature = ogr.Feature(feature_defn)
    feature.SetGeometry(poly)
    feature.SetField("id", 1)
    extent_layer.CreateFeature(feature)
    feature = None
    
    extent_ds = None
    
    

    shutil.copyfile(os.path.join('project_templates','render_atlas.qgs'),os.path.join(unpack_dir,'render_atlas.qgs'))
    #https://gis.stackexchange.com/questions/362636/qgis-on-docker-container-could-not-connect-to-any-x-display
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    os.system('python3 pyqgis_client_atlas.py --project "'+unpack_dir+'/render_atlas.qgs" --layout "atlas_800x800" --output "/data/'+args.prefix+'_region_800x800.png"')
            
    #-----------------------------
    #get bbox for settlement-point.shp
    source_layer_path = os.path.join(unpack_dir,'data','settlement-point.shp')
    assert os.path.isfile(source_layer_path),'not found file for bbox generation '+source_layer_path
    
    ds = gdal.OpenEx(source_layer_path,gdal.OF_READONLY)
    assert ds is not None
    layer = ds.GetLayer()
    assert layer is not None
    layer.SetAttributeFilter('POPULATION IS NOT NULL')
    #search for biggest city
    max_population = 0
    for feature in layer:
        try:
            population = int(feature.GetField('POPULATION'))
        except:
            population = 0
        if population > max_population: max_population = population
    layer.ResetReading()
    where="POPULATION = '"+str(max_population)+"'"
    layer.SetAttributeFilter(where)
    feature = layer.GetNextFeature()
    poly = feature.GetGeometryRef().Buffer(0.01)

    
    # Save poly extent to a new layer
    extent_filename = os.path.join(unpack_dir,'extent_region.geojson')
    extent_driver = ogr.GetDriverByName("GeoJSON")

    if os.path.exists(extent_filename):
        extent_driver.DeleteDataSource(extent_filename)
    extent_ds = extent_driver.CreateDataSource(extent_filename)
    extent_layer = extent_ds.CreateLayer("extent_region", geom_type=ogr.wkbPolygon)
    extent_layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
    feature_defn = extent_layer.GetLayerDefn()
    feature = ogr.Feature(feature_defn)
    feature.SetGeometry(poly)
    feature.SetField("id", 1)
    extent_layer.CreateFeature(feature)
    feature = None
    
    extent_ds = None
    
    

    shutil.copyfile(os.path.join('project_templates','render_atlas.qgs'),os.path.join(unpack_dir,'render_atlas.qgs'))
    #https://gis.stackexchange.com/questions/362636/qgis-on-docker-container-could-not-connect-to-any-x-display
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    os.system('python3 pyqgis_client_atlas.py --project "'+unpack_dir+'/render_atlas.qgs" --layout "atlas_800x800" --output "/data/'+args.prefix+'_city_800x800.png"')
    
    shutil.rmtree(unpack_dir)
    
if __name__ == "__main__":
    main()