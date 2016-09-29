#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Выкачать домики из OSM
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>


import os

import psycopg2
import psycopg2.extras
import pprint
import datetime
from time import gmtime, strftime

global str
# sudo mount -t vboxsf -o uid=user,rw GIS /home/user/GIS



class Processor:


    statistic={}
	    #Define our connection string
    conn_string = "host=localhost user=trolleway dbname=osm_ch3 password=16208 "
     
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
        print "Generate tag filrer string from database for osmfilter call"
        sql="SELECT key, value from tagpref ORDER BY key, value"
        self.cursor.execute(sql)
        self.conn.commit()
        rows = self.cursor.fetchall()
        tags_array=[]            
        for row in rows:
            tags_array.append(''+row[0]+'='+""+row[1]+"")             
        filterstring=' OR '.join(tags_array)

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
psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_line CASCADE;"
psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_point CASCADE;"
psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_polygon CASCADE;"
psql -U trolleway -d osm_ch3 -c "DROP TABLE planet_osm_roads CASCADE;"
        '''
        os.system(cmd)
    
        print 'pbf to o5m'
        cmd='osmconvert {filename}.osm.pbf -o={filename}.o5m'.format(filename=filename)
        print cmd        
        #os.system(cmd)

        print 'o5m tag filtration'
        cmd='osmfilter {filename}.o5m --drop-author --keep="{fl}" --out-o5m >{filename}-filtered.o5m'.format(filename=filename, fl=self.generate_filter_string())
        #print cmd        
        #os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {filename}-filtered.o5m -o={filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        #os.system(cmd)


        print 'pbf to postgis'
        cmd='osm2pgsql -s --create --multi-geometry --latlon --database osm_ch3 --username trolleway -C 12000 --number-processes 3    --style special.style {filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        os.system(cmd)

        #print cmd
        #print "osm2pgsql -s --create --multi-geometry --latlon --database osm_ch3 --username trolleway -C 12000 --number-processes 3   --style special.style  osm/oklahoma-latest.osm.pbf"
        '''

time osmconvert osm/oklahoma-latest.osm.pbf -o=osm/oklahoma-latest.o5m
time osmfilter osm/oklahoma-latest.o5m  --drop-author --out-o5m >osm/oklahoma-latest-da.o5m
time osmconvert osm/oklahoma-latest-da.o5m -o=osm/oklahoma-latest-da.pbf
time osm2pgsql -s --create --multi-geometry --latlon --database osm_ch3 --username trolleway -C 12000 --number-processes 3    --style special.style osm/oklahoma-latest-da.pbf
        '''




    def needed_tags(self):

        if not os.path.exists('output'):
            os.mkdir('output')

        now = datetime.datetime.now()
        print now.isoformat()
        print('Создаются таблицы именно с нужными тегами ')

        print ('Импортируем отдельно выгруженную границу страны, в которой нужно считать точки. Нужно, что бы в квадраты не попали точки находящиеся за Канадской границей. В файле границ не должно быть атрибутов. Выполнение.')
        cmd='ogr2ogr -f "PostgreSQL" PG:"dbname=osm_ch3 user=trolleway" "osm/usa_boundary_osm_buffer.shp" -nln boundary  -nlt MultiPolygon -overwrite'
        print cmd
        os.system(cmd)

        selects=self.generate_sql_query_string()
        


        sql='''
    DROP TABLE IF EXISTS special_point;
    CREATE TABLE special_point AS 
    ( 
    SELECT 
        planet_osm_point.* 

    FROM 
        planet_osm_point
    WHERE 

    ''' + selects+ '''
    )
    ;

        '''

        print('Создаётся таблица точек')
        self.cursor.execute(sql)
        self.conn.commit()

        sql='''
        INSERT INTO special_point (way, '''+self.generate_sql_columns_string()+''') (SELECT ST_PointOnSurface(way) AS way, '''+self.generate_sql_columns_string()+''' FROM planet_osm_polygon WHERE ''' + selects+ '''  ) 
        '''
        print('Добавляются центроиды полигонов POI')
        self.cursor.execute(sql)
        self.conn.commit()






        print 'Создать индексы для точек вручную. Затем нужно вручную отрезать точки, находящиеся за границей страны. Это я не знаю как. В needed_points потом должны быть только точки, попавшие в границу страны'
        '''
ALTER TABLE special_point ADD COLUMN key_column BIGSERIAL PRIMARY KEY;
CREATE INDEX "special_point-index" ON  "special_point" USING GIST (way);
CREATE INDEX "special_point-key_column" ON  "special_point" USING btree (key_column);
VACUUM ANALYZE;
SELECT special_point.osm_id FROM special_point LEFT JOIN boundary  ON ST_Intersects(special_point.way , boundary.wkb_geometry) WHERE boundary.wkb_geometry IS NULL 

        '''

        
        return 0;
        os.system('ogr2ogr -overwrite  -progress -f "ESRI Shapefile" -nlt "POINT" output/point.shp  -lco ENCODING=UTF-8  PG:"host=localhost user=trolleway dbname=osm_ch3 password=16208" -sql "SELECT *  FROM special_point" -a_srs "EPSG:4326" ')
        

        sql='''
    DROP TABLE IF EXISTS special_polygon;
    CREATE TABLE special_polygon AS 
    ( 
    SELECT 
        planet_osm_polygon.* 

    FROM 
        planet_osm_polygon
    WHERE 

    ''' + processor.selects+ '''
    )
    ;

        '''


        print('Создаётся таблица полигонов')
        processor.cursor.execute(sql)
        processor.conn.commit()
        os.system('ogr2ogr -overwrite  -progress  -f "GeoJSON" -nlt "MULTIPOLYGON" output/polygon.geojson  -lco ENCODING=UTF-8  PG:"host=localhost user=trolleway dbname=osm_ch2 password=16208"     -a_srs "EPSG:4326" "special_polygon"')

        '''-where "OGR_GEOMETRY=\'MULTIPOLYGON\'"'''
        sql='''
    DROP TABLE IF EXISTS special_line;
    CREATE TABLE special_line AS 
    ( 
    SELECT 
        planet_osm_line.* 

    FROM 
        planet_osm_line
    WHERE 

    ''' + selects+ '''
    )
    ;

        '''


        print('Создаётся таблица линий')
        cursor.execute(sql)
        conn.commit()
        os.system('ogr2ogr -overwrite  -progress -f "ESRI Shapefile"  output/line.shp  -lco ENCODING=UTF-8  PG:"host=localhost user=trolleway dbname=osm_ch2 password=16208" -sql "SELECT *  FROM special_line" -a_srs "EPSG:4326" ')

        return 0



    def taglist_2db():
        '''

CREATE TABLE tagpref (
    "Preference" text,
    key character varying(50),
    value character varying(50)
);


ALTER TABLE tagpref OWNER TO trolleway;

--
psql -U trolleway -d osm_ch3 -c "DROP TABLE IF EXISTS tagpref"
psql -U trolleway -d osm_ch3 -c "CREATE TABLE tagpref (    "Preference" text,    key character varying(50),    value character varying(50));"
psql -U trolleway -d osm_ch3 -c "ALTER TABLE tagpref OWNER TO trolleway;"
psql -U trolleway -d osm_ch3 -c "COPY tagpref FROM '/home/trolleway/GIS/GIS/project84_osmextract_usa/tagpref.csv' WITH CSV HEADER;"
psql -U trolleway -d osm_ch3 -c "ALTER TABLE tagpref ADD COLUMN uid SERIAL PRIMARY KEY;"
'''
        '''/home/trolleway/GIS/GIS/project84_osmextract_usa/tagpref.csv'''



    def grid_cycle(self):
        srid='3857'

        #координаты взял из qgis ручками

        #США
        xmin=-13854247
        ymax=6340463
        ymin=2781805
        xmax=-7445254

        '''
        #Oklakhoma-edit
        xmin=-11479022
        ymax=6340463
        xmax=-10452195
        ymin=3424009
        '''

        #Начало координат
        x0=0
        y0=0

        stepcounterx=0
        




        #придумать шаг в единицах измерения СК
        xstep=1609.34*1
        ystep=1609.34*1

        #цикл по шагу
        startx=((xmin / xstep)*xstep)+0
        starty=((ymin / ystep)*ystep)+0

        x=startx-xstep
        y=starty-ystep

        totalx=((xmax-xmin) // xstep)+1


        print "Сброс таблицы точек на экспорт"
        sql ='''TRUNCATE  special_point2;TRUNCATE  grid_export;
        '''
        self.cursor.execute(sql)
        self.conn.commit()


        #цикл по столбцам
        while x < xmax:
            x=x+xstep
            stepcounterx=stepcounterx+1

            xnum= x // xstep

            y=starty-ystep
            #цикл по строкам
            print "Обрабатывается столбец "+ str(stepcounterx) +" из " + str(totalx)
            print 'Генерируем одну строку сетки. Она записывается в файл grid.geojson'
            gridgeojson = open('grid.geojson','w')
            gridgeojson.write(self.geojson_header3857)
            while y < ymax:
                y=y+ystep
                ynum=y // ystep

                str1='{ "type": "Feature", "properties": { "id": null, "x": '+str(int(xnum))+', "y": '+str(int(ynum))+' }, "geometry": { "type": "Polygon", "coordinates":'

                
                str2=' [ [ [ {0}, {1} ], [ {2}, {3} ], [ {4}, {5} ], [ {6}, {7} ], [ {0}, {1} ] ] ] '.format( str(x+xstep),str(y),str(x+xstep),str(y+ystep),str(x),str(y+ystep),str(x),str(y) )
                str3="} }, \n"

                #Добавляем в файл geojson один квадрат
                gridgeojson.write(str1+str2+str3)
                #конец цикла по строкам

            #переходим вверх, в цикл по столбцам. Сейчас мы сгенерировали один столбец сетки        
            gridgeojson.write(self.geojson_footer)
            gridgeojson.close()
            print 'Сетка из grid.geojson импортируется в PostGIS одной операцией. В таблице всё время держится по одному столбцу сетки.'
            os.system('ogr2ogr  -f "PostgreSQL" PG:"dbname=osm_ch3 user=trolleway" "grid.geojson" -nln grid4326 -overwrite -t_srs EPSG:4326')
        
            
            #print 'Создается таблица только используемых квадратов'
            sql=''' 
TRUNCATE grid4326used;
INSERT INTO grid4326used (wkb_geometry,x,y) SELECT ST_Intersection(grid_with_pois.wkb_geometry, boundary.wkb_geometry), x,y FROM (SELECT distinct on (grid4326.wkb_geometry) grid4326.wkb_geometry , grid4326.x, grid4326.y  from grid4326  JOIN special_point  ON ST_Covers(grid4326.wkb_geometry , special_point.way)) AS grid_with_pois, boundary  ;'''
            #self.cursor.execute(sql)
            #self.conn.commit()

            print "Рассчитывается bbox столбца"
            sql='''SELECT ST_AsText(ST_SetSRID(ST_Extent(wkb_geometry),4326)) as table_extent FROM grid4326;'''
            self.cursor.execute(sql)
            self.conn.commit()
            rows2 = self.cursor.fetchall()
            bbox=''
            for row2 in rows2:
                bbox=row2[0]


            print "Рассчитывается пересечение bbox столбца со страной (получается прямоугольник, у которого сверху и снизу кривые границы страны"
            sql='''SELECT 
ST_AsText(
ST_Intersection(boundary.wkb_geometry,
ST_GeomFromText(\''''+bbox+'''\',4326)
)
) as table_extent FROM  boundary;'''

            self.cursor.execute(sql)
            self.conn.commit()
            rows2 = self.cursor.fetchall()
            bbox=''
            for row2 in rows2:
                bbox=row2[0]


            print "Рассчитывается пересечение сетки со кусочком страны, обрезанном по столбцу"
            sql='''TRUNCATE grid4326used; INSERT INTO grid4326used (wkb_geometry,x,y) SELECT ST_Intersection(squares_with_pois.wkb_geometry,ST_GeomFromText(\''''+bbox+'''\',4326)),x,y FROM(
SELECT distinct on (grid4326.wkb_geometry) grid4326.wkb_geometry , grid4326.x, grid4326.y  from grid4326  JOIN special_point  ON ST_Covers(grid4326.wkb_geometry , special_point.way)
) AS squares_with_pois'''

            self.cursor.execute(sql)
            self.conn.commit()

            print "Добавляются квадраты в таблицу используемых квадратов сетки"
            sql='''INSERT INTO grid_export (wkb_geometry,x,y) SELECT wkb_geometry,x,y FROM grid4326used'''
            self.cursor.execute(sql)
            self.conn.commit()            

            #конец цикла по столбцам
        
            print "Запуск выборки случайной точки по каждому квадрату"
            self.points_in_grid()
            #return 0












    def generate_grid(self):
        #deprecated
        print "полуавтоматическая генерация сетки. См. комментарии для полного запуска"
        # CREATE TABLE  grid ( id int4, x int4, y int4, geom geometry(POLYGON,3857) ) WITH OIDS; --создать таблицу так

        # http://gis.stackexchange.com/questions/16374/how-to-create-a-regular-polygon-grid-in-postgis
        #каждую часть (потом)
        #преобраовать в 3857
        srid='3857'
        #вытащить xmin ymin из геометрии границ
    
        #координаты взял из qgis ручками
        xmin=-13854247
        ymax=6340463
        ymin=2781805
        xmax=-7445254



        #New York
        xmin=-8879144
        ymax=5627188
        ymin=4935454
        xmax=-7990595


        #oklakhoma
        xmin=-11479022
        ymax=4459167
        xmax=-10452195
        ymin=3924009

        #West half
        xmin=-14050421
        ymax=6224627
        xmax=-10898518
        ymin=4029510
        
        #придумать начало координат
        x0=0
        y0=0
        

        #придумать шаг в единицах измерения СК
        xstep=1609.34*1
        ystep=1609.34*1


        #цикл по шагу
        startx=((xmin / xstep)*xstep)+0
        starty=((ymin / ystep)*ystep)+0

        x=startx-xstep
        y=starty-ystep

        print 'Cетка записывается в файл grid.geojson'
        gridgeojson = open('grid.geojson','w')
        gridgeojson.write(self.geojson_header3857)

        while x < xmax:
            x=x+xstep

            xnum= x // xstep

            y=starty-ystep
            while y < ymax:
                y=y+ystep
                ynum=y // ystep
                
        
                str1='{ "type": "Feature", "properties": { "id": null, "x": '+str(int(xnum))+', "y": '+str(int(ynum))+' }, "geometry": { "type": "Polygon", "coordinates":'

                
                str2=' [ [ [ {0}, {1} ], [ {2}, {3} ], [ {4}, {5} ], [ {6}, {7} ], [ {0}, {1} ] ] ] '.format( str(x+xstep),str(y),str(x+xstep),str(y+ystep),str(x),str(y+ystep),str(x),str(y) )
                str3="} }, \n"


                gridgeojson.write(str1+str2+str3)




        #определить, какой № квадрата в этой точке
        #insert into
        gridgeojson.write(self.geojson_footer)
        gridgeojson.close()
        print 'Сетка из grid.geojson импортируется в PostGIS одной операцией'
        os.system('ogr2ogr -progress -f "PostgreSQL" PG:"dbname=osm_ch3 user=trolleway" "grid.geojson" -nln grid -overwrite ')


        print 'перепроецирeтся в 4326'
        sql=        '''
DROP TABLE if exists grid4326;
CREATE TABLE grid4326 AS 
  SELECT ST_Transform(wkb_geometry,4326) AS wkb_geometry , x, y
  FROM grid;'''
        self.cursor.execute(sql)
        self.conn.commit()
        print 'Создать индексы для сетки вручную'
        '''
CREATE INDEX "grid4326-index" ON  "grid4326" USING GIST (wkb_geometry);
VACUUM ANALYZE;
        '''
        print 'Создать таблицу только используемых квадратов вручную'
        '''
DROP TABLE if exists grid4326used;
CREATE TABLE grid4326used AS SELECT distinct on (grid4326.wkb_geometry) grid4326.wkb_geometry , grid4326.x, grid4326.y  from grid4326  JOIN special_point  ON ST_Covers(grid4326.wkb_geometry , special_point.way);
DROP INDEX IF EXISTS "grid4326used-index";
CREATE INDEX "grid4326used-index" ON  "grid4326used" USING GIST (wkb_geometry);

VACUUM ANALYZE;
        '''



        return 0
















    def points_in_grid(self):

        pref=0
        tags_by_pref={}

        while pref<3:
            pref=pref+1      
            print "Генерируется фрагмент запроса для тегов с приоритетом "+str(pref)  

            sql='''SELECT key, value FROM 
    tagpref
    WHERE tagpref."preference"=\'''' +str(pref) +'''\'
    Order by tagpref."preference" DESC'''
            self.cursor.execute(sql)
            self.conn.commit()
            rows = self.cursor.fetchall()
            tags_array=[]
                        
            for row in rows:
                tags_array.append('"'+row[0]+'"='+"'"+row[1]+"'")  


            
            tags_by_pref[pref]=" \n OR ".join(tags_array)






        sql_columns = self.generate_sql_columns_string()      


        print 'Таблица точек на экспорт тут не сбрасывается'



        sql="SELECT wkb_geometry, CONCAT(x,'-',y) AS id from grid4326used ORDER BY x,y  "
        self.cursor.execute(sql)
        self.conn.commit()
        rows = self.cursor.fetchall()
        for row in rows:
            print "Квадрат ", row[1]

            '''

            '''

            #запрос наличия объектов в квадрате

            sql = "select COUNT(*)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry)  AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' LIMIT 1"
            self.cursor.execute(sql)
            self.conn.commit()
            rows2 = self.cursor.fetchall()

            records_in_element_total=0
            for row2 in rows2:
                records_in_element_total=row2[0]
            print "Количество записей в квадрате: ", records_in_element_total
            if records_in_element_total < 1:
                continue;

            #запрос количества объектов в квадрате с заданным приоритетом
            priority=3
            sql = "select COUNT(p2.wkb_geometry)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' LIMIT 1"
            self.cursor.execute(sql)
            self.conn.commit()
            rows2 = self.cursor.fetchall()

            records_in_element=0
            for row2 in rows2:
                records_in_element=row2[0]
            print "Количество записей с приоритетом = 3 в квадрате: ", records_in_element

            if  records_in_element > 0 :
                print "Вставляем в квадрат запись с приоритетом 3"
                sql =" INSERT INTO special_point2 (wkb_geometry,  name,"+sql_columns+") select p1.way, name, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"'  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"
                self.cursor.execute(sql)
                self.conn.commit()
            else:
                priority=2
                sql = "SELECT COUNT(p2.wkb_geometry)  \n FROM special_point p1, grid4326used p2 \n WHERE st_within (p1.way, p2.wkb_geometry) AND (\n" +tags_by_pref[priority]+ ") \n AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' LIMIT 1"
                self.cursor.execute(sql)
                self.conn.commit()
                rows2 = self.cursor.fetchall()
                records_in_element=0
                for row2 in rows2:
                    records_in_element=row2[0]
                print "Количество записей с приоритетом = 2 в квадрате: ", records_in_element
                if  records_in_element > 0 :
                                print "Вставляем в квадрат запись с приоритетом 2"
                                sql =" INSERT INTO special_point2 (wkb_geometry, name, "+sql_columns+") select p1.way, name, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"'  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"

                                self.cursor.execute(sql)
                                self.conn.commit()
                else:
                    priority=1
                    sql = "select COUNT(p2.wkb_geometry)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' LIMIT 1"
                    self.cursor.execute(sql)
                    self.conn.commit()
                    rows2 = self.cursor.fetchall()
                    records_in_element=0
                    for row2 in rows2:
                        records_in_element=row2[0]
                    print "Количество записей с приоритетом = 1 в квадрате: ", records_in_element
                    if  records_in_element > 0 :
                                    print "Вставляем в квадрат запись с приоритетом 1"
                                    sql =" INSERT INTO special_point2 (wkb_geometry, name, "+sql_columns+") select p1.way, name, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"'  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"
                                    

                                    self.cursor.execute(sql)
                                    self.conn.commit()
                    
            

            '''select * from special_point p1, grid4326 p2 where st_within (p1.way, p2.geom)
AND concat(p2.x,'-',p2.y)='-9-2' 

UPDATE special_point
SET attr = hstore('shop',special_point.shop)
WHERE special_point.shop IS NOT NULL;

            '''


    

    def tag_stat(selects):
        #не нужно
        
        sql='''
    select count(*), aerialway, aeroway, amenity, barrier, building, craft, historic, leisure, military, place, public_transport, railway, shop, sport, tourism
     from special_point
    group by aerialway, aeroway, amenity, barrier, building, craft, historic, leisure, military, place, public_transport, railway, shop, sport, tourism

    order by count

    ;
            '''


        print('Создаётся таблица полигонов')
        cursor.execute(sql)
        conn.commit()

        #не нужно
    '''
create table grid_used as
select p2.*  from boundary, grid4326 p2 
where ST_Intersects(boundary.wkb_geometry , p2.geom)  
    ogr2ogr -f "PostgreSQL" PG:"dbname=osm_ch3 user=trolleway" "source/state new york.geojson" -nln boundary -overwrite
    '''

'''
get boundaries
time osmfilter north-america-latest.o5m --keep= --keep-relations="admin_level=2" --out-o5m >osms/admin_level2.o5m


'''
