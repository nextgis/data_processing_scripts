#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Рассчёт зон транспортной доступности
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2017, NextGIS <info@nextgis.com>




import os

import psycopg2
import psycopg2.extras
import pprint
import datetime
import requests
from time import gmtime, strftime





import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Convert partially overlapped polygons to touching polygons with common border in PostGIS',
            formatter_class=PrettyFormatter)
    parser.add_argument('-pg', '--pg_conn', type=str, default='',
                        help='PostGIS connection string to osm dump')

    parser.add_argument('-p', '--input', type=str, default='areas.geojson',
                        help='Polygon file')
    parser.add_argument('-o', '--output', type=str, default='polygons_smoothed.geojson',
                        help='Out file')


    parser.epilog = \
        '''Samples: 
            Take overlapping polygons, calculate and create file withouth intersection
%(prog)s --pg_conn "dbname=osm_ch3" --input areas.shp --output polygons_smoothed.geojson
''' \
        % {'prog': parser.prog}
    return parser






parser = argparser_prepare()
args = parser.parse_args()
     

print ('Importing')
cmd='ogr2ogr -f "PostgreSQL" PG:"{pg_conn}" "{filename}" -nln overlap2touch1  -nlt Polygon -overwrite'.format(pg_conn=pg_conn,filename=args.input)
print cmd
os.system(cmd)

conn_string = conn_string
conn = psycopg2.connect(conn_string)
conn.autocommit = True #для vaccuum

# conn.cursor will return a cursor object, you can use this cursor to perform queries
cursor = conn.cursor()



sql='''


SELECT shop_id,
    COALESCE(
    ST_Difference(
        wkb_geometry, 
        (SELECT ST_Union(b.wkb_geometry) FROM overlap2touch1 b 
            WHERE ST_Intersects(a.wkb_geometry,b.wkb_geometry) AND a.shop_id < b.shop_id)),a.wkb_geometry) AS wkb_geometry
FROM overlap2touch1 AS a;
'''


print ('Exporting')
cmd='ogr2ogr -f "PostgreSQL" -f "{output}" PG:"{pg_conn}"  -sql "{sql}"  -nlt Polygon -overwrite'.format(pg_conn=pg_conn,output=args.output,sql=sql)
print cmd
os.system(cmd)

