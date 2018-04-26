#!/bin/bash



set -x
: '
dist='2000'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 10000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3

dist='2500'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 10000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3

dist='3000'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 10000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
dist='3500'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 10000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
dist='4000'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 2000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
dist='4500'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 2000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
dist='5000'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 3000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
dist='5500'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 3300 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
dist='6000'
time python transport_attraction_zones.py --pg_conn "dbname=gis" --distance $dist --calc_distance 40000 --overlap overlapped
ogr2ogr -f gpkg -overwrite calc_$dist.gpkg PG:"dbname=gis" costs3
'
ts=$(date +"%Y-%m-%d")
zip -R backup_step1_$ts '*.gpkg'

ogrmerge.py -f VRT -single -o merged.vrt *.gpkg -src_layer_field_name val

mkdir output
ogr2ogr -overwrite -progress -f "PostgreSQL" "PG:host=localhost port=5432 user=trolleway dbname=gis password=trolleway" -nln smoothing -lco GEOMETRY_NAME=wkb_geometry merged.vrt 


SQL=$(cat <<-ENDTEXT
--deleting holes
UPDATE smoothing AS maintable SET wkb_geometry = fillingholes.wkb_geometry
FROM (
SELECT ogc_fid, ST_Collect(ST_MakePolygon(wkb_geometry)) As wkb_geometry
FROM (
    SELECT ogc_fid, ST_ExteriorRing((ST_Dump(wkb_geometry)).geom) As wkb_geometry
    FROM smoothing
    ) s
GROUP BY ogc_fid) AS fillingholes 
WHERE fillingholes.ogc_fid = maintable.ogc_fid;
ENDTEXT
)
ogrinfo "PG:host=localhost port=5432 user=trolleway dbname=gis password=trolleway" -sql "$SQL"
#smoothing, simplifying
rm output/sum.geojson
ogr2ogr -overwrite -progress -f "GeoJSON" output/sum.geojson "PG:host=localhost port=5432 user=trolleway dbname=gis password=trolleway"  -sql "SELECT ST_SimplifyPreserveTopology(ST_Buffer(wkb_geometry::geography,100)::geometry,0.001) AS wkb_geometry, left(right(val,-5),4)::integer/1000 AS distance,shop_id FROM smoothing"

