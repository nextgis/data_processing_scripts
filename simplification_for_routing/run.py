#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: 
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016-2018, NextGIS <info@nextgis.com>

import config

import os
import psycopg2
import psycopg2.extras

import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Simplification of OSM for routing. \n\nOpen pbf, simplify roads by remove all points beetwen crossings, save as new pbf. \nOriginal length save as "len_geography" attribute (store in real meters)',
            formatter_class=PrettyFormatter)

    parser.add_argument('-s', '--source', type=str,help='Source pbf',required=True)
    parser.add_argument('-d', '--destination', type=str,help='Destination shapefile.',required=True)

    parser.epilog = \
        '''Samples:
%(prog)s --source ru-mow.osm.pbf --destination simplified.osm.pbf

''' \
        % {'prog': parser.prog}
    return parser


class Processor:

    #Define our connection string
    conn_string = config.psycopg2_postgresql_connection_string
    pgpass=config.pgpass #for osm2pgsql

     
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True #для vaccuum
     
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()










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




        #os.system('export PGPASS='+self.pgpass)
        #os.system('export PGPASSWORD='+self.pgpass)
        os.environ['PGPASSWORD'] = str(self.pgpass)
    


        print 'pbf to postgis'
        cmd='osm2pgsql {osm2pgsql_config}  --create --slim  --create --multi-geometry --latlon    --number-processes 3 --style special.style {filename}'.format(osm2pgsql_config=config.osm2pgsql,filename=filename)     
        os.system(cmd)
        



    def postgis2geojson(self,table):
        if os.path.exists(table+'.geojson'):
            os.remove(table+'.geojson')

        cmd='''
    ogr2ogr -fieldTypeToString All -f GeoJSON '''+table+'''.geojson    \
      "PG:'''+self.ogr2ogr_pg+'''" "'''+table+'''" 
        '''
        print cmd
        os.system(cmd)   



    def data_export(self,filename):
        '''

▀▀▀▝▘▀▝▘▐▌▀▘  ▝▀▘ ▀     ▀▀    ▝▀▘  ▀▀▘ ▝▘ ▝▘     ▀▀ ▝▀▘    ▝▘   ▝▀▘  ▀▀▀   ▀▀  ▀▀ ▀▀▀ ▀▀▘ 

        '''
        print 'Export frop PostGIS'

        cmd = 'ogr2ogr -progress -nlt linestring -lco ENCODING=UTF-8 -fieldTypeToString all -overwrite -t_srs EPSG:4326 -f "ESRI Shapefile" simplified.shp  PG:"{ogr2ogr_pg}" "routes_split_by_intersections" '.format(ogr2ogr_pg=config.ogr2ogr_pg)
        print cmd        
        os.system(cmd)

        cmd = 'python ogr2osm/ogr2osm.py --force --id 999999999 --positive-id --add-version simplified.shp '.format(ogr2ogr_pg=config.ogr2ogr_pg)
        print cmd        
        os.system(cmd)

        cmd = 'osmconvert simplified.osm -o={filename}'.format(ogr2ogr_pg=config.ogr2ogr_pg,filename=filename)
        print cmd        
        os.system(cmd)

        #os.unlink('simplified.osm')

    def simplify(self):
        sql = '''
DROP TABLE IF EXISTS routes_split_by_intersections;

CREATE 

TABLE routes_split_by_intersections  

AS(
select  (st_dump(st_union(way))).geom AS geom 
from planet_osm_line);
--ALTER TABLE routes_split_by_intersections ADD COLUMN id SERIAL PRIMARY KEY;

ALTER TABLE routes_split_by_intersections ADD COLUMN len_geography real;
UPDATE routes_split_by_intersections SET len_geography = ST_Length(geom::geography);
UPDATE routes_split_by_intersections SET geom = ST_MakeLine(ST_StartPoint(geom),ST_EndPoint(geom));


'''

        self.cursor.execute(sql)
        self.conn.commit()




if __name__ == '__main__':

    parser = argparser_prepare()
    args = parser.parse_args()

    processor = Processor()
    processor.osmimport(args.source)
    processor.simplify()
    processor.data_export(args.destination)




