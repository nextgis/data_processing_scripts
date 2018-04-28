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


    def __init__(self):


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


