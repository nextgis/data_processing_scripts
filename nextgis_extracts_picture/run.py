#!/usr/bin/python3
# -*- coding: utf8 -*-

import os
import shutil
import argparse
from osgeo import gdal, ogr

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Export QGIS map composer layout to png using pyqgis',
            formatter_class=PrettyFormatter)
    parser.add_argument('extract',   help='Path to extract zip archive')


    return parser


def main():
    parser = argparser_prepare()
    args = parser.parse_args()
    
    #unpack extract
    unpack_dir = 'extract'
    
    #get bbox 
    highways_layer_path = os.path.join(unpack_dir,'data','highway-line.shp')
    assert os.path.isfile(highways_layer_path),'not found file for bbox generation '+highways_layer_path
    
    ds = gdal.OpenEx(highways_layer_path,gdal.OF_READONLY)
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
    
    # Save extent to a new Shapefile
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
    
    

    shutil.copyfile(os.path.join(project_templates,'render_atlas.qgs'),os.path.join(unpack_dir,'render_atlas.qgs')
    #https://gis.stackexchange.com/questions/362636/qgis-on-docker-container-could-not-connect-to-any-x-display
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    os.system('python3 pyqgis_client_atlas.py --project "extract/render_atlas.qgs" --layout "atlas_800x800" --output "spoon_RU-AST.png"')
    
    
if __name__ == "__main__":
    main()