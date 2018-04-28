#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: выкачивание с openaerialmap
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2018, NextGIS <info@nextgis.com>


import os
import requests
import urllib




class Processor:

    statistic={}
        #Define our connection string

    connection = None
    cursor = None      
     
        # get a connection, if a connect cannot be made an exception will be raised here


    
    geojson_header3857='''{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3857" } },
                                                                                
"features": [

    '''
    geojson_footer='''
]
}
    '''


    def __init__(self, pg_conn=None):
        self.pg_conn = pg_conn
        self.conn = psycopg2.connect(pg_conn)
        self.conn.autocommit = True #для vaccuum
     
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        self.cursor = self.conn.cursor()
        



    def oam_download(self):
        
        endpoint = 'http://api.openaerialmap.org/meta'
        query = endpoint + '?bbox=37.3193,55.4899,37.9457,56.0097&gsd_to=1&gsd_from=0.001&acquisition_from=2014-01-01&acquisition_to=2018-01-01&limit=100'
        
        response = urllib.urlopen(query)
        data = json.loads(response.read())
        
        for scene in 


import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35


    parser = argparse.ArgumentParser(description='''Ge
    ''',
            formatter_class=PrettyFormatter)


    

    parser.add_argument('-pg', '--pg_conn', type=str, default='',
                        help='PostGIS connection string to osm dump')
    parser.add_argument('-s', '--starts', type=str, default='starts.geojson',
                        help='Point geodata file')
    parser.add_argument('-d', '--distance', type=str, default='1000',
                        help='Distance in meters')
    parser.add_argument('-c', '--calc_distance', type=str, default='1000',
                        help='Distance for initial selection of calc points. Ideally should be same as distance, but for big city may be 50%% of distance to spped up')
    parser.add_argument('--overlap',
                    default='independed',
                    choices=[ 'overlapped', 'independed'],
                    help='overlapped: return overlapped polygons; independed: use only distance from nearest start, return touched polygons')



    parser.epilog = \
        '''Samples: 
%(prog)s --pg_conn "dbname=osm_ch3" --filename starts.shp
''' \
        % {'prog': parser.prog}
    return parser


parser = argparser_prepare()
args = parser.parse_args()
processor=Processor(pg_conn=args.pg_conn)
#processor.generate_filter_string() #Generate string with tags for osmfilter
#processor.osmimport('moscow_russia')
processor.pointsimport(args.starts)
processor.isodistances(distance=args.distance,cutdistance=args.calc_distance,overlap=args.overlap)
#processor.isodistances2geojson(isodistances)


