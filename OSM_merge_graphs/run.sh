#!/bin/bash





echo "Reading config...."
source config.cfg


tempdir=tmp
echo $tempdir
rm -rf $tempdir
mkdir $tempdir

osmfile="source.osm.pbf"
file1="30.geojson"
file2="36.geojson"

ogr2ogr -progress -overwrite -geomfield wkb_geometry  -f "ESRI Shapefile" -where "highway IS NOT NULL"  $tempdir/union.shp $osmfile lines


ogr2ogr -progress -update  -append -geomfield wkb_geometry -geomfield wkb_geometry -t_srs EPSG:4326 -f "ESRI Shapefile" -nlt LINESTRING -where "OGR_GEOMETRY='LineString'"  $tempdir/union.shp $file1
ogr2ogr -progress -update  -append -geomfield wkb_geometry -geomfield wkb_geometry -t_srs EPSG:4326 -f "ESRI Shapefile" -nlt LINESTRING -where "OGR_GEOMETRY='LineString'"  $tempdir/union.shp $file2


ogr2ogr -progress -overwrite -f "PostgreSQL" PG:"host=$host dbname=$dbname user=$user" $tempdir/union.shp -nln joining
psql --host $host --username $user --dbname=$dbname -a -f split_lines_by_intersections.sql

psql --host $host --username $user --dbname=$dbname -a -f insert_tags.sql

rm graph.geojson
ogr2ogr -progress -overwrite -f "ESRI Shapefile"  graph.shp PG:"host=$host dbname=$dbname user=$user" "split"
ogr2ogr -progress -overwrite -f "ESRI Shapefile"  graph.geojson PG:"host=$host dbname=$dbname user=$user" "split"
python ogr2osm/ogr2osm.py --force --id 999999999 --positive-id graph.shp 
osmconvert graph.osm -o=graph.osm.pbf
