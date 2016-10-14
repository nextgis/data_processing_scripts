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
    ogr2ogr_pg = config.ogr2ogr_pg
    pgpass=config.pgpass #for osm2pgsql
    osm2pgsql_style=config.osm2pgsql_style
    
    ngw_url = config.ngw_url
    ngw_login = config.ngw_login
    ngw_password = config.ngw_password
    ngw_res_id = config.ngw_res_id
    
     
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



    def generate_filter_string(self):
        print "Generate tag filrer for osmfilter call"
        filterstring = 'natural=tree'

        return filterstring







    def osmimport(self,filename):
        '''
▄▄▄                           ▗▄▖  ▗▄▖ ▗▄ ▄▖               ▗▄▄▖                ▄▄ ▄▄▄ ▗▄▖ 
▀█▀                    ▐▌     █▀█ ▗▛▀▜ ▐█ █▌    ▐▌         ▐▛▀▜▖          ▐▌  █▀▀▌▀█▀▗▛▀▜ 
 █ ▐█▙█▖▐▙█▙  ▟█▙ █▟█▌▐███   ▐▌ ▐▌▐▙   ▐███▌   ▐███ ▟█▙    ▐▌ ▐▌▟█▙ ▗▟██▖▐███▐▌    █ ▐▙   
 █ ▐▌█▐▌▐▛ ▜▌▐▛ ▜▌█▘   ▐▌    ▐▌ ▐▌ ▜█▙ ▐▌█▐▌    ▐▌ ▐▛ ▜▌   ▐██▛▐▛ ▜▌▐▙▄▖▘ ▐▌ ▐▌▗▄▖ █  ▜█▙ 
 █ ▐▌█▐▌▐▌ ▐▌▐▌ ▐▌█    ▐▌    ▐▌ ▐▌   ▜▌▐▌▀▐▌    ▐▌ ▐▌ ▐▌   ▐▌  ▐▌ ▐▌ ▀▀█▖ ▐▌ ▐▌▝▜▌ █    ▜▌
▄█▄▐▌█▐▌▐█▄█▘▝█▄█▘█    ▐▙▄    █▄█ ▐▄▄▟▘▐▌ ▐▌    ▐▙▄▝█▄█▘   ▐▌  ▝█▄█▘▐▄▄▟▌ ▐▙▄ █▄▟▌▄█▄▐▄▄▟▘
▀▀▀▝▘▀▝▘▐▌▀▘  ▝▀▘ ▀     ▀▀    ▝▀▘  ▀▀▘ ▝▘ ▝▘     ▀▀ ▝▀▘    ▝▘   ▝▀▘  ▀▀▀   ▀▀  ▀▀ ▀▀▀ ▀▀▘ 

        '''
        print 'Import OSM to PostGIS'




        sql='''
        DROP TABLE IF EXISTS planet_osm_line CASCADE;
        DROP TABLE IF EXISTS planet_osm_point CASCADE;
        DROP TABLE IF EXISTS planet_osm_polygon CASCADE;
        DROP TABLE IF EXISTS planet_osm_roads CASCADE;

        '''
        self.cursor.execute(sql)
        self.conn.commit()

        os.system('export PGPASS='+self.pgpass)
    

        print 'o5m tag filtration'
        cmd='osmfilter {filename}.o5m --drop-author --keep= --keep-nodes="{fl}"   --out-o5m >{filename}-filtered.o5m'.format(filename=filename, fl=self.generate_filter_string())
        print cmd        
        os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {filename}-filtered.o5m -o={filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        os.system(cmd)


        print 'pbf to postgis'
        cmd='osm2pgsql {osm2pgsql_config}  --slim  --create --multi-geometry --latlon   -C 12000 --number-processes 3 --style {osm2pgsql_style} {filename}-filtered.pbf'.format(osm2pgsql_config=config.osm2pgsql,filename=filename,osm2pgsql_style=self.osm2pgsql_style)
        print cmd        
        os.system(cmd)


    def postgis2geojson(self,table):
        if os.path.exists(table+'.geojson'):
            os.remove(table+'.geojson')

        cmd='''
    ogr2ogr -fieldTypeToString Integer -f GeoJSON '''+table+'''.geojson    \
      "PG:'''+self.ogr2ogr_pg+'''" "'''+table+'''" 
        '''
        print cmd
        os.system(cmd)        


