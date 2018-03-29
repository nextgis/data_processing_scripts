#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Расчёт зон транспортной доступности
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2017, NextGIS <info@nextgis.com>


import os

import psycopg2
import psycopg2.extras
import pprint
import datetime
import requests
from time import gmtime, strftime

global str

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


    def generate_filter_string(self):
        print "Generate tag filrer string from database for osmfilter call"

        filterstring = 'building='
        return filterstring

    def generate_sql_query_string(self):
        print "Generate tag filrer string from database for sql queries"
        sql="SELECT key, value from tagpref ORDER BY key, value "
        self.cursor.execute(sql)
        self.conn.commit()
        rows = self.cursor.fetchall()
        tags_array=[]            
        for row in rows:
            tags_array.append('"'+row[0]+'"='+"'"+row[1]+"'")             
        filterstring="\n OR ".join(tags_array)

        return filterstring


    def generate_sql_columns_string(self):
        print "Generate tag filrer string from database for sql columns list"
        sql="SELECT DISTINCT key from tagpref ORDER BY key "
        self.cursor.execute(sql)
        self.conn.commit()
        rows = self.cursor.fetchall()
        tags_array=[]           
        for row in rows:
            tags_array.append('"'+row[0]+'"')             
        filterstring=' , '.join(tags_array)

        return filterstring

    def osmimport(self,filename):
        print 'Import OSM to PostGIS'


        cmd='''
#psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_line CASCADE;"
#psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_point CASCADE;"
#psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_polygon CASCADE;"
#psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_roads CASCADE;"
        '''
        os.system(cmd)
    
        print 'pbf to o5m'
        cmd='osmconvert {filename}.osm.pbf -o={filename}.o5m'.format(filename=filename)
        print cmd        
        os.system(cmd)

        print 'o5m tag filtration'
        cmd='osmfilter {filename}.o5m --drop-author --keep="{fl}" --out-o5m >{filename}-filtered.o5m'.format(filename=filename, fl=self.generate_filter_string())
        print cmd        
        os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {filename}-filtered.o5m -o={filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        os.system(cmd)


        print 'pbf to postgis'
        cmd='osm2pgsql -s --create --multi-geometry --latlon --database processing_osm_ch1 --username trolleway -C 2000 --number-processes 3    --style special.style {filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        os.system(cmd)

        #print cmd

    def pointsimport(self,filename):



        print ('Импортируем точки стартов')
        cmd='ogr2ogr -f "PostgreSQL" PG:"{pg_conn}" "{filename}" -nln starts  -nlt Point -overwrite'.format(filename=filename,pg_conn=self.pg_conn)
        print cmd
        os.system(cmd)


    def isodistances(self,distance,cutdistance=2000):
        print ('Генерация полигонов isodistance по зданиям')


        #Создаём таблицу равноудалённости

        print('Создаётся таблица точек')
        sql='''
        DROP TABLE IF EXISTS isodistances;
        CREATE TABLE isodistances
        (
          --ogc_fid integer NOT NULL DEFAULT nextval('grid4326_ogc_fid_seq'::regclass),
          id character varying,
          wkb_geometry geometry(Polygon,4326),
          distance bigint
        --  CONSTRAINT isodistances_pkey PRIMARY KEY (ogc_fid)
        --)

        );
        ALTER TABLE isodistances
          OWNER TO trolleway;

        -- Index: public.grid4326_wkb_geometry_geom_idx

        -- DROP INDEX public.grid4326_wkb_geometry_geom_idx;

        CREATE INDEX isodistances_wkb_geometry_geom_idx
          ON isodistances
          USING gist
          (wkb_geometry);



                '''
        self.cursor.execute(sql)
        self.conn.commit()

        sql='''
        DROP TABLE IF EXISTS costs;'''

       

        self.cursor.execute(sql)
        self.conn.commit()


        sql='''
CREATE TABLE costs
(
id    serial primary key,
a        integer not null,
b        integer not null,
cost_max integer
);'''

        
        self.cursor.execute(sql)
        self.conn.commit()

        #Для каждой точки старта
        sql='''SELECT num AS num,ST_X(wkb_geometry), ST_Y(wkb_geometry) FROM starts ORDER BY num::integer;'''
        self.cursor.execute(sql)
        self.conn.commit()
        startpoints = self.cursor.fetchall()
        startPoint=''
        print sql
        for startpoint in startpoints:
            print 'start num={num} distance={targetdistance}'.format(num=str(startpoint[0]),targetdistance=distance ) 
            


            #Генерируем круг в 5 километров
            #Берём все входяшие в него здания
            #Для каждого здания делаем точку на здании
            sql='''
            --temporary table with circle around start, later we take all building in this circle.
            --it should be faster than query all buildings by distance
            DROP TABLE IF EXISTS querycircle;
            CREATE TEMPORARY TABLE querycircle ON COMMIT DROP AS
                SELECT ST_Buffer(starts.wkb_geometry::geography,{targetdistance}) AS wkb_geography,
                1 AS id
                FROM starts 
                WHERE starts.num::varchar={startsnum}::varchar;

            DROP TABLE IF EXISTS calcpoints;
            CREATE TABLE calcpoints AS
SELECT
ST_PointOnSurface(planet_osm_polygon.way) AS wkb_geometry ,
0::Bigint AS cost,
planet_osm_polygon.osm_id AS osm_id   
FROM
planet_osm_polygon, 
querycircle 
WHERE 
ST_Intersects(planet_osm_polygon.way::geography,querycircle.wkb_geography)
;'''


            ''' предыдущий вариант, отбор зданий по расстоянию
            DROP TABLE IF EXISTS calcpoints;
            CREATE TABLE calcpoints AS
             SELECT
ST_PointOnSurface(planet_osm_polygon.way)
 AS wkb_geometry ,
 0::Bigint AS cost,

 planet_osm_polygon.osm_id AS osm_id   
FROM
    planet_osm_polygon, starts 

WHERE 
--ST_Distance_Sphere(planet_osm_polygon.way, starts.wkb_geometry) <= {cutdistance}
ST_Distance(ST_PointOnSurface(planet_osm_polygon.way)::geography, starts.wkb_geometry::geography) BETWEEN 0 AND {targetdistance}
AND starts.num::varchar={startsnum}::varchar
'''
            sql=sql.format(startsnum=startpoint[0],targetdistance=distance, cutdistance=cutdistance)


            
            self.cursor.execute(sql)
            self.conn.commit()
			
            

            #Для каждой точки здания считаем расстояние
            sql = 'SELECT ST_X(wkb_geometry), ST_Y(wkb_geometry),osm_id FROM calcpoints'
            self.cursor.execute(sql)
            self.conn.commit()
            finishpoints= self.cursor.fetchall()
            #r = requests.session()

            sql_big=''
            for finishpoint in finishpoints:
                #print 'Подсчёт расстояния для точки '+ finishpoint[0] + ' ' + finishpoint[1]

                osrm_query='http://127.0.0.1:5000/route/v1/driving/{startpoint_coord_string};{finishpoint_coord_string}'.format(startpoint_coord_string=str(startpoint[1])+','+str(startpoint[2]),finishpoint_coord_string=str(finishpoint[0])+','+str(finishpoint[1]))
                r = requests.get(osrm_query)
                osrm_response = r.json()
                distanceAB = osrm_response["routes"][0]["distance"]

                '''
                osrm_query='http://127.0.0.1:5000/route/v1/driving/{finishpoint_coord_string};{startpoint_coord_string}'.format(startpoint_coord_string=str(startpoint[1])+','+str(startpoint[2]),finishpoint_coord_string=str(finishpoint[0])+','+str(finishpoint[1]))
                r = requests.get(osrm_query)
                osrm_response = r.json()
                distanceBA = osrm_response["routes"][0]["distance"]
				'''

                #print distance
                #if (int(distance)<cutdistance):
                #    sql = 'UPDATE calcpoints SET cost='+str(max(distanceAB,distanceBA)) + 'WHERE osm_id = '+str(finishpoint[2])
                #    self.cursor.execute(sql)

                distanceBA=0

                if (int(max(distanceAB,distanceBA))<int(distance)):
                	sql = 'INSERT INTO costs (a,b,cost_max) VALUES ({a}, {b},{cost});'
                	sql=sql.format(a=startpoint[0],b=str(finishpoint[2]),cost=str(max(distanceAB,distanceBA)))
                	sql_big += sql
            
            self.cursor.execute(sql_big)
            self.conn.commit()

            #Теперь у точек записалось расстояние от 1 до dist_max. А те что дальше dist_max - мы пропускали, у них cost=0, удаляем их.
            #sql = 'DELETE FROM costs WHERE cost_max<10000;'
            #self.cursor.execute(sql)
            #self.conn.commit()

        #print 'Дальше открывайте в qgis таблицу calcpoints, и обрабатывайте её процесингом'

        sql = '''
            DROP TABLE IF EXISTS costs2;
            CREATE TABLE costs2 AS

select ST_Centroid(planet_osm_polygon.way) AS wkb_geometry,  costs.a,subquery.b,subquery.min FROM (
SELECT b,min(cost_max) as min
FROM costs
WHERE cost_max<{distance}
GROUP BY b ) as subquery JOIN costs ON subquery.b=costs.b AND subquery.min=costs.cost_max
JOIN planet_osm_polygon ON planet_osm_polygon.osm_id=costs.b;


            DROP TABLE IF EXISTS costs3;
            CREATE TABLE costs3 AS

            SELECT ST_ConcaveHull(ST_Union(wkb_geometry),0.6) AS wkb_geometry, a as shop_id FROM costs2 group by shop_id;

'''
        sql=sql.format(distance=distance)
        self.cursor.execute(sql)
        self.conn.commit()

            #Если расстояние меньше 5000, то добавляем точку в новую таблицу
            #Делаем для точек concave hull
            
            #sql='''INSERT INTO isodistances (wkb_geometry, distance) SELECT ST_ConcaveHull(ST_Union(wkb_geometry),0.6) AS wkb_geometry, 2000 AS distance FROM calcpoints WHERE cost <=2000'''
            #self.cursor.execute(sql)
            #self.conn.commit()

            
            #Делаем буфер на пару метров вокруг convave hull
            #опционально: примазываем к буферу здания, на которые попадают точки.
            #Называем это равноудалённостью, добавляем в таблицу





import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35


    parser = argparse.ArgumentParser(description='''Generating in PostGIS correspondence matrix and non-intersection transport attraction zones using OSRM.
        Рассчёт в PostGIS матрицы корреспонденций и непересекающихся зон транспортного тяготения.
Requires: 
    1. PostGIS database в pg_conn
    2. ogr-compatible point file with "num" attribute --starts
    3. Database should have layer planet_osm_polygons - distances will calc to PointOnSurface of these polygons. /*В базе должны быть только дома, а если будут ещё границы городов - то будут левые точки*/
    4. ORSM server, listening to his default address.

Outputs:
    1. В PostGIS создаётся таблица costs - матрица корреспонденций. 
        Сейчас считается длина от точки старта до каждого дома в радиусе calc_distance, 
        если оно меньше distance, то в матрицу записывается минимальное значение (длина от ближайшего старта). 
        Можно считать ещё длину сразу в обе стороны.
    2. В PostGIS создаётся таблица costs3 - полигоны, описывающие вогнутым многоугольником зоны, тяготеющие к одному из стартов.
        Эти зоны могут друг на друга накладываться, но совсем немножко.

    Дальше эти зоны можно сгладить в QGIS используя buffer_smooth.model и потом сделать общие границы скриптом overlapped2touching.py    


    где-то расстояния могут быть захардкодены внутри.

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
processor.isodistances(distance=args.distance,cutdistance=args.calc_distance)
#processor.isodistances2geojson(isodistances)


