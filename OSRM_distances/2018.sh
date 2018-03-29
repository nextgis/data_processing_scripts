#!/bin/bash

set -x
#dist='2000'
#time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance 10000 $dist --calc_distance 10000
#ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3

#dist='2500'
#time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 10000
#ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3

#dist='3000'
#time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 10000
#ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3
#dist='3500'
#time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 10000
#ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3


dist='4000'
time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 2000
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3
dist='4500'
time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 2000
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3
dist='5000'
time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 3000
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3
dist='5500'
time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 3300
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3
dist='6000'
time python transport_attraction_zones.py --pg_conn "dbname=processing_osm_ch1" --distance $dist --calc_distance 40000
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=processing_osm_ch1" costs3
