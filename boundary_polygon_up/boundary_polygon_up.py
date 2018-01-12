#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: osm-extracts
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2018, NextGIS <info@nextgis.com>

# open boundary-polygon.shp, for each feature add 3 attributes with names of upper administrative objects


import os


from osgeo import ogr, gdal
from osgeo import osr

#import urllib

#import zipfile
import sys
#import requests
import progressbar
#import json

import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='',
            formatter_class=PrettyFormatter)

    parser.add_argument('-s', '--source', type=str,help='Source shapefile',required=True)
    parser.add_argument('-d', '--destination', type=str,help='Destination shapefile',required=True)

    parser.epilog = \
        '''Samples:
%(prog)s 

''' \
        % {'prog': parser.prog}
    return parser


class processor:




    accounts = {}

    def __init__(self,cfg):
        pass



    def boundary_polygonup(self,path,destination):

        # ogrsql
        '''


python process.py --path ../../test/data/boundary-polygon.shp

ogr2ogr -f "ESRI Shapefile" ../../test/result.shp ../../test/data/boundary-polygon.shp -dialect sqlite \
-sql "select ST_buffer(Geometry,0.001) from boundary-polygon"

        '''


        from osgeo import ogr
        '''
        ogr_ds = ogr.Open(path)
        TEST=3
        sql = "SELECT upper_polygon.NAME  FROM \"boundary-polygon\"  current_polygon, \"boundary-polygon\"  upper_polygon ON ST_Intersects(ST_PointOnSurface(current_polygon.GEOMETRY), upper_polygon.GEOMETRY)=1 WHERE ADMIN_LVL = '6'"
        sql = "SELECT current_polygon.NAME AS name_c, upper_polygon.NAME,ST_Intersects(ST_Centroid(current_polygon.GEOMETRY), upper_polygon.GEOMETRY) AS val  FROM \"boundary-polygon\"  current_polygon, \"boundary-polygon\"  upper_polygon ON 1=1 WHERE current_polygon.ADMIN_LVL = '6' AND upper_polygon.ADMIN_LVL = '4' LIMIT 100"
        sql = "select GEOMETRY, NAME as name from \"boundary-polygon\" WHERE ADMIN_LVL = '6'"
        layer = ogr_ds.ExecuteSQL(sql,None,'SQLITE')
        '''

        defaultDestination = os.path.dirname(path) , "test.shp"

        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.isfile(path) == False:
            raise IOError('file {path} does not exist.'.format(path=path))
            quit()  
        dataSource = driver.Open(path, 0)
        layer = dataSource.GetLayer()

        '''
        #get physical filename for destination
        #By default in emporary folder

        temp_destination_folder = ''
        if destination is None:
        	import tempfile
        	temp_destination_folder = tempfile.mkdtemp()
        '''

        # Save to a new Shapefile
        outShapefile = destination
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        outLayer = outDataSource.CreateLayer("test", srs=srs, geom_type=ogr.wkbMultiPolygon,options=["ENCODING=UTF-8"])


        # Add input Layer Fields to the output Layer
        inLayerDefn = layer.GetLayerDefn()
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)
        # Add special fields
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L1',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L2',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L3',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L4',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L5',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L6',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L7',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L8',ogr.OFTString))
        outLayer.CreateField(ogr.FieldDefn('ADMIN_L9',ogr.OFTString))



        # Get the output Layer's Feature Definition
        outLayerDefn = outLayer.GetLayerDefn()


        # Also open source layer several times for search
        # Apply attribute filter for search upper names
        dataSource_admlevel1 = driver.Open(path, 0)
        layer_admlevel1 = dataSource_admlevel1.GetLayer()
        layer_admlevel1.SetAttributeFilter("ADMIN_LVL = '1'")
        dataSource_admlevel2 = driver.Open(path, 0)
        layer_admlevel2 = dataSource_admlevel2.GetLayer()
        layer_admlevel2.SetAttributeFilter("ADMIN_LVL = '2'")
        dataSource_admlevel3 = driver.Open(path, 0)
        layer_admlevel3 = dataSource_admlevel3.GetLayer()
        layer_admlevel3.SetAttributeFilter("ADMIN_LVL = '3'")
        dataSource_admlevel4 = driver.Open(path, 0)
        layer_admlevel4 = dataSource_admlevel4.GetLayer()
        layer_admlevel4.SetAttributeFilter("ADMIN_LVL = '4'")
        dataSource_admlevel5 = driver.Open(path, 0)
        layer_admlevel5 = dataSource_admlevel5.GetLayer()
        layer_admlevel5.SetAttributeFilter("ADMIN_LVL = '5'")
        dataSource_admlevel6 = driver.Open(path, 0)
        layer_admlevel6 = dataSource_admlevel6.GetLayer()
        layer_admlevel6.SetAttributeFilter("ADMIN_LVL = '6'")
        dataSource_admlevel7 = driver.Open(path, 0)
        layer_admlevel7 = dataSource_admlevel7.GetLayer()
        layer_admlevel7.SetAttributeFilter("ADMIN_LVL = '7'")
        dataSource_admlevel8 = driver.Open(path, 0)
        layer_admlevel8 = dataSource_admlevel8.GetLayer()
        layer_admlevel8.SetAttributeFilter("ADMIN_LVL = '8'")
        dataSource_admlevel9 = driver.Open(path, 0)
        layer_admlevel9 = dataSource_admlevel9.GetLayer()
        layer_admlevel9.SetAttributeFilter("ADMIN_LVL = '9'")




        # Add features to the ouput Layer
        bar = progressbar.ProgressBar(widgets=[
    ' [', progressbar.Timer(), '] ',
    progressbar.Bar(),
    ' (', progressbar.ETA(), ') ',
])

        for i in bar(range(0, layer.GetFeatureCount())):
        #for i in range(0, layer.GetFeatureCount()):
            # Get the input Feature

            inFeature = layer.GetFeature(i)

            geom = inFeature.GetGeometryRef()

            #Perform a spatial query
            query_geometry = geom.PointOnSurface().Buffer(0.009) 
            layer_admlevel1.SetSpatialFilter(query_geometry)
            layer_admlevel2.SetSpatialFilter(query_geometry)
            layer_admlevel3.SetSpatialFilter(query_geometry)
            layer_admlevel4.SetSpatialFilter(query_geometry)
            layer_admlevel5.SetSpatialFilter(query_geometry)
            layer_admlevel6.SetSpatialFilter(query_geometry)
            layer_admlevel7.SetSpatialFilter(query_geometry)
            layer_admlevel8.SetSpatialFilter(query_geometry)
            layer_admlevel9.SetSpatialFilter(query_geometry)

            ##according to documentation, it return "all features whose envelope (as returned by OGRGeometry::getEnvelope()) overlaps the envelope of the spatial filter". 
            #may be faster to ..rect

            #Get name of upper region
            layer_admlevel1.ResetReading()
            upFeature_admlevel1 = layer_admlevel1.GetNextFeature()            
            layer_admlevel2.ResetReading()
            upFeature_admlevel2 = layer_admlevel2.GetNextFeature()            
            layer_admlevel3.ResetReading()
            upFeature_admlevel3 = layer_admlevel3.GetNextFeature()            
            layer_admlevel4.ResetReading()
            upFeature_admlevel4 = layer_admlevel4.GetNextFeature()            
            layer_admlevel5.ResetReading()
            upFeature_admlevel5 = layer_admlevel5.GetNextFeature()            
            layer_admlevel6.ResetReading()
            upFeature_admlevel6 = layer_admlevel6.GetNextFeature()            
            layer_admlevel7.ResetReading()
            upFeature_admlevel7 = layer_admlevel7.GetNextFeature()            
            layer_admlevel8.ResetReading()
            upFeature_admlevel8 = layer_admlevel8.GetNextFeature()            
            layer_admlevel9.ResetReading()
            upFeature_admlevel9 = layer_admlevel9.GetNextFeature()            
        


            # Create output Feature
            outFeature = ogr.Feature(outLayerDefn)
            # Add field values from input Layer

            for f in range(0, inLayerDefn.GetFieldCount()):
                outFeature.SetField(outLayerDefn.GetFieldDefn(f).GetNameRef(), inFeature.GetField(f))
            #Add name of upper region
            current_ADMIN_LVL = inFeature.GetField('ADMIN_LVL')
            if current_ADMIN_LVL in ['2','3','4','5','6','7','8','9','10'] and upFeature_admlevel1 is not None: 
                outFeature.SetField('ADMIN_L1',upFeature_admlevel1.GetField('NAME'))
            if current_ADMIN_LVL in ['3','4','5','6','7','8','9','10'] and upFeature_admlevel2 is not None: 
                outFeature.SetField('ADMIN_L2',upFeature_admlevel2.GetField('NAME'))
            if current_ADMIN_LVL in ['4','5','6','7','8','9','10'] and upFeature_admlevel3 is not None: 
                outFeature.SetField('ADMIN_L3',upFeature_admlevel3.GetField('NAME'))
            if current_ADMIN_LVL in ['5','6','7','8','9','10'] and upFeature_admlevel4 is not None: 
                outFeature.SetField('ADMIN_L4',upFeature_admlevel4.GetField('NAME'))
            if current_ADMIN_LVL in ['6','7','8','9','10'] and upFeature_admlevel5 is not None: 
                outFeature.SetField('ADMIN_L5',upFeature_admlevel5.GetField('NAME'))
            if current_ADMIN_LVL in ['7','8','9','10'] and upFeature_admlevel6 is not None:
                outFeature.SetField('ADMIN_L6',upFeature_admlevel6.GetField('NAME'))
            if current_ADMIN_LVL in ['8','9','10'] and upFeature_admlevel7 is not None:
                outFeature.SetField('ADMIN_L7',upFeature_admlevel7.GetField('NAME'))
            if current_ADMIN_LVL in ['9','10'] and upFeature_admlevel8 is not None:
                outFeature.SetField('ADMIN_L8',upFeature_admlevel8.GetField('NAME'))
            if current_ADMIN_LVL in ['10'] and upFeature_admlevel9 is not None:
                outFeature.SetField('ADMIN_L9',upFeature_admlevel9.GetField('NAME'))




            # Set geometry as copy of source
            outFeature.SetGeometry(geom)

            #inFeature = None

            outLayer.CreateFeature(outFeature)
            outFeature = None
            upFeature_admlevel1 = None
            upFeature_admlevel2 = None
            upFeature_admlevel3 = None
            upFeature_admlevel4 = None
            upFeature_admlevel5 = None
            upFeature_admlevel6 = None
            upFeature_admlevel7 = None
            upFeature_admlevel8 = None
            upFeature_admlevel9 = None



        # Save and close DataSources
        inDataSource = None
        outDataSource = None


        '''
        layer.SetAttributeFilter("ADMIN_LVL = '6'")
        for feature in layer:
            current_polygon_geomery = ogr.CreateGeometryFromWkb(wkb)
            current_polygon_centroid = current_polygon_geomery.Centroid()
            print feature.GetField("NAME"), ' - '
            #print feature.GetField("NAME")
            #print feature.GetField("val")
        layer.ResetReading()
        ogr_ds.Destroy()
        '''




if __name__ == '__main__':

    parser = argparser_prepare()
    args = parser.parse_args()
         
    cfg=dict()



    processor=processor(cfg=cfg)

    processor.boundary_polygonup(path=args.source,destination=args.destination)
