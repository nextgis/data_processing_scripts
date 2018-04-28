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
        
        for scene in data:
            print scene['uuid']


import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35


    parser = argparse.ArgumentParser(description='''Ge
    ''',
            formatter_class=PrettyFormatter)


    

    #parser.add_argument('-d', '--distance', type=str, default='1000',
    #                    help='Distance in meters')



    parser.epilog = \
        '''Samples: 
%(prog)s 
''' \
        % {'prog': parser.prog}
    return parser


parser = argparser_prepare()
args = parser.parse_args()
processor=Processor()
processor.oam_download()


