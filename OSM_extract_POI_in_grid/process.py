#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Специальное вытаскивание данных из OSM по специальному алгоритму
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>

'''
 ▗▄▖  ▗▄▖ ▗▄ ▄▖           ▗▄▄▖                ▄▄ ▄▄▄ ▗▄▖              ▄▄ █ ▗▄▖             
 █▀█ ▗▛▀▜ ▐█ █▌           ▐▛▀▜▖          ▐▌  █▀▀▌▀█▀▗▛▀▜             ▐▛▀ ▀ ▝▜▌ ▐▌          
▐▌ ▐▌▐▙   ▐███▌   ▐▄▖     ▐▌ ▐▌▟█▙ ▗▟██▖▐███▐▌    █ ▐▙      ▐▄▖     ▐█████  ▐▌▐███ ▟█▙ █▟█▌
▐▌ ▐▌ ▜█▙ ▐▌█▐▌    ▝▀▙▖   ▐██▛▐▛ ▜▌▐▙▄▖▘ ▐▌ ▐▌▗▄▖ █  ▜█▙     ▝▀▙▖    ▐▌  █  ▐▌ ▐▌ ▐▙▄▟▌█▘  
▐▌ ▐▌   ▜▌▐▌▀▐▌    ▗▄▛▘   ▐▌  ▐▌ ▐▌ ▀▀█▖ ▐▌ ▐▌▝▜▌ █    ▜▌    ▗▄▛▘    ▐▌  █  ▐▌ ▐▌ ▐▛▀▀▘█   
 █▄█ ▐▄▄▟▘▐▌ ▐▌   ▐▀▘     ▐▌  ▝█▄█▘▐▄▄▟▌ ▐▙▄ █▄▟▌▄█▄▐▄▄▟▘   ▐▀▘      ▐▌▗▄█▄▖▐▙▄▐▙▄▝█▄▄▌█   
 ▝▀▘  ▀▀▘ ▝▘ ▝▘           ▝▘   ▝▀▘  ▀▀▀   ▀▀  ▀▀ ▀▀▀ ▀▀▘             ▝▘▝▀▀▀▘ ▀▀ ▀▀ ▝▀▀ ▀                                                                                            
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
        filterstring=" OR ".join(tags_array)

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
        #self.cursor.execute(sql)
        #self.conn.commit()

    
        print 'pbf to o5m'
        cmd='osmconvert {filename}.osm.pbf -o={filename}.o5m'.format(filename=filename)
        print cmd        
        #os.system(cmd)

        print 'o5m tag filtration'
        cmd='osmfilter {filename}.o5m --drop-author --keep="{fl}" --out-o5m >{filename}-filtered.o5m'.format(filename=filename, fl=self.generate_filter_string())
        print cmd        
        #os.system(cmd)

        print 'o5m to pbf'
        cmd='osmconvert {filename}-filtered.o5m -o={filename}-filtered.pbf'.format(filename=filename)
        print cmd        
        #os.system(cmd)


        print 'pbf to postgis'
        cmd='osm2pgsql {osm2pgsql_config}  -s --create --multi-geometry --latlon   -C 12000 --number-processes 3 --style osm2pgsql.style {filename}-filtered.pbf'.format(osm2pgsql_config=config.osm2pgsql,filename=filename)
        print cmd        
        os.system(cmd)






    def needed_tags(self):

        if not os.path.exists('output'):
            os.mkdir('output')

        now = datetime.datetime.now()
        print now.isoformat()
        print('Создаются таблицы именно с нужными тегами ')

        #print ('Импортируем отдельно выгруженную границу страны, в которой нужно считать точки. Нужно, что бы в квадраты не попали точки находящиеся за Канадской границей. В файле границ не должно быть атрибутов. Выполнение.')
        #cmd='ogr2ogr -f "PostgreSQL" PG:"dbname=processing_osm_ch3 user=trolleway" "osm/usa_boundary_osm_buffer.shp" -nln boundary  -nlt MultiPolygon -overwrite'
        #print cmd
        #os.system(cmd)

        selects=self.generate_sql_query_string()
        


        sql='''
        TRUNCATE TABLE special_point;
        '''
        self.cursor.execute(sql)
        self.conn.commit()

        sql='''INSERT INTO special_point (way, name, amenity) (SELECT starbucks.wkb_geometry AS way, brand AS name, 'cafe' AS amenity  FROM starbucks JOIN boundary_optimized ON ST_Intersects(starbucks.wkb_geometry, boundary_optimized.wkb_geometry)

   ) ;'''
        print('Добавляются точки starbucks внутри страны')
        self.cursor.execute(sql)
        self.conn.commit()


        sql='''
        INSERT INTO special_point (way, name, osm_id,'''+self.generate_sql_columns_string()+''') (SELECT way AS way, name, CONCAT('n',"osm_id")::varchar(20) AS osm_id, '''+self.generate_sql_columns_string()+''' FROM planet_osm_point JOIN boundary_optimized ON ST_Intersects(planet_osm_point.way, boundary_optimized.wkb_geometry) WHERE ''' + selects+ '''  ) 
        '''
        print sql
        print('Добавляются  POI из таблицы точек')
        self.cursor.execute(sql)
        self.conn.commit()



        sql='''
        INSERT INTO special_point (way, name, osm_id,'''+self.generate_sql_columns_string()+''') (SELECT ST_PointOnSurface(way) AS way, name,  CONCAT('p',"osm_id")::varchar(20) AS osm_id, '''+self.generate_sql_columns_string()+''' FROM planet_osm_polygon JOIN boundary_optimized ON ST_Intersects(planet_osm_polygon.way, boundary_optimized.wkb_geometry) WHERE ''' + selects+ '''  ) 
        '''
        print('Добавляются центроиды полигонов POI')
	print sql
        self.cursor.execute(sql)
        self.conn.commit()
	
	






        print 'Проверь, есть ли индексы'
        '''
ALTER TABLE special_point ADD COLUMN key_column BIGSERIAL PRIMARY KEY;
CREATE INDEX "special_point-index" ON  "special_point" USING GIST (way);
CREATE INDEX "special_point-key_column" ON  "special_point" USING btree (key_column);
VACUUM ANALYZE;
SELECT special_point.osm_id FROM special_point LEFT JOIN boundary  ON ST_Intersects(special_point.way , boundary.wkb_geometry) WHERE boundary.wkb_geometry IS NULL 

        '''

        
        return 0;
        
        '''
Эксперимент.
http://gis.stackexchange.com/questions/19832/how-to-fix-performance-problem-in-postgis-st-intersects
Из таблицы с мультиполигоном границы - сделать таблицу где каждый остров - отдельный объект, и навесить индекс



CREATE TABLE boundary_optimized as SELECT (ST_Dump(wkb_geometry)).geom as wkb_geometry FROM boundary;

-- It is always great to put a primary key on the table
ALTER table boundary_optimized ADD Column gid serial PRIMARY KEY;

-- Create the index
CREATE INDEX idx_boundary_optimized_geom
on boundary_optimized
USING gist(wkb_geometry);

-- To give the database some information about how the index looks
vacuum analyze boundary_optimized;

-- Then you go:
SELECT DISTINCT ON (userid) userid ,ST_AsText(position), timestamp  
FROM table1, big polygon WHERE ST_Intersects ( big_polygon.geom,position) 
ORDER BY userid, timestamp desc;



        '''




    def grid_cycle(self):
        '''
          █     ▗▖                        ▗▄▖      
          ▀     ▐▌                        ▝▜▌      
 ▟█▟▌█▟█▌██   ▟█▟▌            ▟██▖▝█ █▌▟██▖▐▌  ▟█▙ 
▐▛ ▜▌█▘   █  ▐▛ ▜▌           ▐▛  ▘ █▖█▐▛  ▘▐▌ ▐▙▄▟▌
▐▌ ▐▌█    █  ▐▌ ▐▌           ▐▌    ▐█▛▐▌   ▐▌ ▐▛▀▀▘
▝█▄█▌█  ▗▄█▄▖▝█▄█▌           ▝█▄▄▌  █▌▝█▄▄▌▐▙▄▝█▄▄▌
 ▞▀▐▌▀  ▝▀▀▀▘ ▝▀▝▘            ▝▀▀   █  ▝▀▀  ▀▀ ▝▀▀ 
 ▜█▛▘                              █▌              
                     ▀▀▀▀▀                         

        '''
        srid='3857'

        #координаты взял из qgis ручками

        #США
        xmin=-13854247
        ymax=6340463
        ymin=2781805
        xmax=-7445254

        #Аляска
        xmin=-20014504
        ymax=11612294
        ymin=-1671038
        xmax=2003083



        #Начало координат
        x0=0
        y0=0

        stepcounterx=0
        




        #придумать шаг в единицах измерения СК
        xstep=1609.34*0.25
        ystep=1609.34*0.25

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

        #print "Добавляются все starbucks по миру, кроме тех что в границе USA"
        #sql ='''INSERT INTO special_point2 (wkb_geometry, name, amenity) (SELECT t1.wkb_geometry AS way, t1.brand AS name, 'cafe' AS amenity  FROM starbucks t1, boundary t2 WHERE ST_Disjoint(t1.wkb_geometry, t2.wkb_geometry)  ) ;'''
        #self.cursor.execute(sql)
        #self.conn.commit()

        #цикл по столбцам
        while x < xmax:
            x=x+xstep
            stepcounterx=stepcounterx+1

            xnum= x // xstep

            y=starty-ystep
		
	    #Проверка: есть ли POI в этом столбце	
            gridColumnWKT='{x1} {y1},{x2} {y1},{x2} {y2},{x1} {y2}, {x1} {y1}'.format(x1=x, x2=x+xstep,y1=ymax, y2=ymin)
            sql='''SELECT COUNT(special_point.*) AS cnt FROM special_point WHERE ST_Intersects(way,  ST_Transform(ST_GeomFromText(\'POLYGON(('''+gridColumnWKT+'''))\',3857),4326))'''
            #print sql
            self.cursor.execute(sql)
            self.conn.commit()
            rows = self.cursor.fetchall()
            bbox=''
            for row in rows:
                cnt=row[0]
            if str(cnt)=='0':
                #print 'В этот столбец сетки не попадают POI, пропуск'
                continue
		
            #цикл по строкам
            print "Обрабатывается столбец "+ str(stepcounterx) +" из " + str(totalx)
            print 'Генерируем один столбец сетки. Он записывается в файл grid.geojson'
            gridgeojson = open('grid.geojson','w')
            gridgeojson.write(self.geojson_header3857)
            while y < ymax:
                y=y+ystep
                ynum=y // ystep
		
		
                gridColumnWKT='{0} {1}, {2} {3} ,  {4} {5} , {6} {7} , {0} {1}'.format( str(x+xstep),str(y),str(x+xstep),str(y+ystep),str(x),str(y+ystep),str(x),str(y) )
                sql='''SELECT COUNT(special_point.*) AS cnt FROM special_point WHERE ST_Intersects(way,  ST_Transform(ST_GeomFromText(\'POLYGON(('''+gridColumnWKT+'''))\',3857),4326))'''
                #print sql
                self.cursor.execute(sql)
                self.conn.commit()
                rows = self.cursor.fetchall()
                bbox=''
                for row in rows:
                    cnt=row[0]
                if str(cnt)=='0':
                    #print 'В эту ячейку сетки не попадают POI, пропуск'
                    continue
			
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
            os.system('ogr2ogr  -f "PostgreSQL" PG:"{ogr2ogr_pg}" "grid.geojson" -nln grid4326 -overwrite -t_srs EPSG:4326'.format(ogr2ogr_pg=config.ogr2ogr_pg))
        
            
            print 'Создается таблица только используемых квадратов'
            sql=''' 
TRUNCATE grid4326used;
INSERT INTO grid4326used (wkb_geometry,x,y) SELECT distinct on (grid4326.wkb_geometry) grid4326.wkb_geometry , grid4326.x, grid4326.y  
from grid4326  JOIN special_point  ON ST_Intersects( special_point.way,grid4326.wkb_geometry )  ;'''
	    print sql
            self.cursor.execute(sql)
            self.conn.commit()
	    quit()

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
) as table_extent FROM  boundary_optimized AS boundary
WHERE not ST_IsEmpty(ST_Intersection(boundary.wkb_geometry,
ST_GeomFromText(\''''+bbox+'''\',4326)
)) '''
            print sql

            self.cursor.execute(sql)
            self.conn.commit()
            rows2 = self.cursor.fetchall()
            bbox=''
            for row2 in rows2:
                bbox=row2[0]

            if bbox=='GEOMETRYCOLLECTION EMPTY':
                print 'Этот столбец сетки не попадает в страну, пропуск'
                continue
            if bbox=='':
                print 'Этот столбец сетки не попадает в страну, пропуск'
                continue	 

            print "Рассчитывается пересечение сетки со кусочком страны, обрезанном по столбцу"
            sql='''TRUNCATE grid4326used; INSERT INTO grid4326used (wkb_geometry,x,y) SELECT ST_Intersection(squares_with_pois.wkb_geometry,ST_GeomFromText(\''''+bbox+'''\',4326)),x,y FROM(
SELECT distinct on (grid4326.wkb_geometry) grid4326.wkb_geometry , grid4326.x, grid4326.y  FROM grid4326  JOIN special_point  ON ST_Covers(grid4326.wkb_geometry , special_point.way)
) AS squares_with_pois'''

            sql='''TRUNCATE grid4326used; INSERT INTO grid4326used (wkb_geometry,x,y) SELECT grid4326.wkb_geometry,grid4326.x,grid4326.y
FROM grid4326 JOIN 
(
SELECT  special_point.way
FROM special_point
WHERE ST_Intersects(special_point.way,ST_GeomFromText(\''''+bbox+'''\',4326))
) pois_in_grid
ON ST_Intersects(grid4326.wkb_geometry,pois_in_grid.way)
'''

            print sql

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

            if str(int(xnum))=='-49077':
                quit()
	



    def points_in_grid(self):
        '''
                                                                               
            █                             █                            █     ▗▖
            ▀        ▐▌                   ▀                            ▀     ▐▌
▐▙█▙  ▟█▙  ██  ▐▙██▖▐███▗▟██▖            ██  ▐▙██▖            ▟█▟▌█▟█▌██   ▟█▟▌
▐▛ ▜▌▐▛ ▜▌  █  ▐▛ ▐▌ ▐▌ ▐▙▄▖▘             █  ▐▛ ▐▌           ▐▛ ▜▌█▘   █  ▐▛ ▜▌
▐▌ ▐▌▐▌ ▐▌  █  ▐▌ ▐▌ ▐▌  ▀▀█▖             █  ▐▌ ▐▌           ▐▌ ▐▌█    █  ▐▌ ▐▌
▐█▄█▘▝█▄█▘▗▄█▄▖▐▌ ▐▌ ▐▙▄▐▄▄▟▌           ▗▄█▄▖▐▌ ▐▌           ▝█▄█▌█  ▗▄█▄▖▝█▄█▌
▐▌▀▘  ▝▀▘ ▝▀▀▀▘▝▘ ▝▘  ▀▀ ▀▀▀            ▝▀▀▀▘▝▘ ▝▘            ▞▀▐▌▀  ▝▀▀▀▘ ▝▀▝▘
▐▌                                                            ▜█▛▘             
                                ▀▀▀▀▀                ▀▀▀▀▀                     

        '''

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
            sql = "select COUNT(p2.wkb_geometry)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS NOT NULL LIMIT 1"
            self.cursor.execute(sql)
            self.conn.commit()
            rows2 = self.cursor.fetchall()
            records_in_element=0
            for row2 in rows2:
                records_in_element=row2[0]
            print "Количество записей с приоритетом = 3 AND name IS NOT NULL в квадрате: ", records_in_element
            if  records_in_element > 0 :
                print "Вставляем в квадрат запись с приоритетом 3"
                sql =" INSERT INTO special_point2 (wkb_geometry,  name, osm_id,"+sql_columns+") select p1.way, name, osm_id, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS NOT NULL  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"
                self.cursor.execute(sql)
                self.conn.commit()
            else:
                sql = "select COUNT(p2.wkb_geometry)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS NULL LIMIT 1"
                self.cursor.execute(sql)
                self.conn.commit()
                rows2 = self.cursor.fetchall()
                records_in_element=0
                for row2 in rows2:
                    records_in_element=row2[0]
                print "Количество записей с приоритетом = 3 AND name IS NULL в квадрате: ", records_in_element
                if  records_in_element > 0 :
                    print "Вставляем в квадрат запись с приоритетом 3"
                    sql =" INSERT INTO special_point2 (wkb_geometry,  name, osm_id,"+sql_columns+") select p1.way, name, osm_id, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS  NULL  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"
                    self.cursor.execute(sql)
                    self.conn.commit()
                else:

                    priority=2
                    sql = "SELECT COUNT(p2.wkb_geometry)  \n FROM special_point p1, grid4326used p2 \n WHERE st_within (p1.way, p2.wkb_geometry) AND (\n" +tags_by_pref[priority]+ ") \n AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS NOT NULL LIMIT 1"
                    self.cursor.execute(sql)
                    self.conn.commit()
                    rows2 = self.cursor.fetchall()
                    records_in_element=0
                    for row2 in rows2:
                        records_in_element=row2[0]
                    print "Количество записей с приоритетом = 2 AND p1.name IS NOT NULL в квадрате: ", records_in_element
                    if  records_in_element > 0 :
                                    print "Вставляем в квадрат запись с приоритетом 2"
                                    sql =" INSERT INTO special_point2 (wkb_geometry, name, osm_id, "+sql_columns+") select p1.way, name, osm_id, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS NOT NULL  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"

                                    self.cursor.execute(sql)
                                    self.conn.commit()
                    else:
                        sql = "SELECT COUNT(p2.wkb_geometry)  \n FROM special_point p1, grid4326used p2 \n WHERE st_within (p1.way, p2.wkb_geometry) AND (\n" +tags_by_pref[priority]+ ") \n AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS  NULL LIMIT 1"
                        self.cursor.execute(sql)
                        self.conn.commit()
                        rows2 = self.cursor.fetchall()
                        records_in_element=0
                        for row2 in rows2:
                            records_in_element=row2[0]
                        print "Количество записей с приоритетом = 2 AND p1.name IS  NULL в квадрате: ", records_in_element
                        if  records_in_element > 0 :
                                        print "Вставляем в квадрат запись с приоритетом 2"
                                        sql =" INSERT INTO special_point2 (wkb_geometry, name, osm_id, "+sql_columns+") select p1.way, name, osm_id, "+sql_columns+" from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS  NULL  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"

                                        self.cursor.execute(sql)
                                        self.conn.commit()
                        else:
                            priority=1
                            sql = "select COUNT(p2.wkb_geometry)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS NOT NULL LIMIT 1"
                            self.cursor.execute(sql)
                            self.conn.commit()
                            rows2 = self.cursor.fetchall()
                            records_in_element=0
                            for row2 in rows2:
                                records_in_element=row2[0]
                            print "Количество записей с приоритетом = 1  AND p1.name IS NOT NULL в квадрате: ", records_in_element
                            if  records_in_element > 0 :
                                            print "Вставляем в квадрат запись с приоритетом 1"
                                            sql =" INSERT INTO special_point2 (wkb_geometry, name, "+sql_columns+") select p1.way, name, "+sql_columns+" from special_point p1, grid4326used p2 WHERE st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"'  AND p1.name IS NOT NULL  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"
                                            
                                            self.cursor.execute(sql)
                                            self.conn.commit()
                            else:
                                sql = "select COUNT(p2.wkb_geometry)  from special_point p1, grid4326used p2 where st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"' AND p1.name IS  NULL LIMIT 1"
                                self.cursor.execute(sql)
                                self.conn.commit()
                                rows2 = self.cursor.fetchall()
                                records_in_element=0
                                for row2 in rows2:
                                    records_in_element=row2[0]
                                print "Количество записей с приоритетом = 1  AND p1.name IS NULL в квадрате: ", records_in_element
                                if  records_in_element > 0 :
                                                print "Вставляем в квадрат запись с приоритетом 1"
                                                sql =" INSERT INTO special_point2 (wkb_geometry, name, osm_id, "+sql_columns+") select p1.way, name, osm_id, "+sql_columns+" from special_point p1, grid4326used p2 WHERE st_within (p1.way, p2.wkb_geometry) AND (" +tags_by_pref[priority]+ ") AND  concat(p2.x,'-',p2.y)='"+str(row[1])+"'  AND p1.name IS NULL  OFFSET floor(random()*"+str(records_in_element)+") LIMIT 1"
                                                
                                                self.cursor.execute(sql)
                                                self.conn.commit()
                    
            
