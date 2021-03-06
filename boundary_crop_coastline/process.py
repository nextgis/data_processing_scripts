#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Специальное вытаскивание данных из OSM по специальному алгоритму
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>

'''
                                                                                       
'''

import os

import psycopg2
import psycopg2.extras
import pprint
import datetime
from time import gmtime, strftime

import config

global str



class Processor:


    statistic={}
	    #Define our connection string
    conn_string = config.psycopg2_postgresql_connection_string
     
	    # print the connection string we will use to connect

     
	    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True #для vaccuum
     
	    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()

    
    geojson_header3857='''{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3857" } },
                                                                                
"features": [

    '''
    geojson_footer='''
]
}
    '''


    cstep=0


    cstep+=1
    print('Инициализируется скрипт обработки')


    
    selects='''

    '''



    def data_import(self,filename):
        '''

▀▀▀▝▘▀▝▘▐▌▀▘  ▝▀▘ ▀     ▀▀    ▝▀▘  ▀▀▘ ▝▘ ▝▘     ▀▀ ▝▀▘    ▝▘   ▝▀▘  ▀▀▀   ▀▀  ▀▀ ▀▀▀ ▀▀▘ 

        '''
        print 'Import coastline to PostGIS'

        cmd = 'ogr2ogr -progress -nlt multipolygon -overwrite -t_srs EPSG:4326 -f "PostgreSQL" PG:"{ogr2ogr_pg}" ../../simplifed/land_polygons_z5_4326.shp -nln coastline'.format(ogr2ogr_pg=config.ogr2ogr_pg)
        print cmd        
        os.system(cmd)

        cmd = 'ogr2ogr -progress -nlt multipolygon -overwrite -t_srs EPSG:4326 -f "PostgreSQL" PG:"{ogr2ogr_pg}" ../../boundary-polygon.shp -nln boundary'.format(ogr2ogr_pg=config.ogr2ogr_pg)
        print cmd        
        os.system(cmd)


        cmd = 'ogr2ogr -progress -nlt multipolygon -overwrite -t_srs EPSG:4326 -f "PostgreSQL" PG:"{ogr2ogr_pg}" ../../lakes-ru/lakes-ru.shp -nln lakes'.format(ogr2ogr_pg=config.ogr2ogr_pg)
        print cmd        
        os.system(cmd)

    def process(self,b=None):
        '''
                                                                               


            '''
        sql = '''DROP TABLE IF EXISTS boundary_inner; '''    
        self.cursor.execute(sql)
        self.conn.commit()    

        sql='''CREATE TABLE boundary_inner AS SELECT boundary.OSM_ID, boundary.NAME, boundary.ADMIN_LVL AS admin_leve
     , CASE 
       WHEN ST_CoveredBy(boundary.wkb_geometry, coastline.wkb_geometry) 
       THEN boundary.wkb_geometry 
       ELSE 
        ST_Multi(
          ST_Intersection(boundary.wkb_geometry, coastline.wkb_geometry)
          ) END AS geom 
     FROM boundary  
       INNER JOIN coastline 
        ON (ST_Intersects(boundary.wkb_geometry, coastline.wkb_geometry) 
          AND NOT ST_Touches(boundary.wkb_geometry, coastline.wkb_geometry) );'''


        self.cursor.execute(sql)
        self.conn.commit()

    def data_export(self,filename):
        '''

▀▀▀▝▘▀▝▘▐▌▀▘  ▝▀▘ ▀     ▀▀    ▝▀▘  ▀▀▘ ▝▘ ▝▘     ▀▀ ▝▀▘    ▝▘   ▝▀▘  ▀▀▀   ▀▀  ▀▀ ▀▀▀ ▀▀▘ 

        '''
        print 'Export frop PostGIS'

        cmd = 'ogr2ogr -progress -nlt multipolygon -lco ENCODING=UTF-8 -fieldTypeToString all -overwrite -t_srs EPSG:4326 -f "ESRI Shapefile" boundary-polygon-cropped.shp  PG:"{ogr2ogr_pg}" "boundary_inner" '.format(ogr2ogr_pg=config.ogr2ogr_pg)
        print cmd        
        os.system(cmd)

        cmd = 'rm -f boundary-polygon-cropped.7z'
        print cmd        
        os.system(cmd)

        cmd = '7z a boundary-polygon-cropped.7z boundary-polygon-cropped.*'
        print cmd        
        os.system(cmd)

