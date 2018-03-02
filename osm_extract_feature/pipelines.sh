#!/bin/bash 

name='pipelines'
osmconvert current.osm.pbf -o=russia.o5m
osmfilter russia.o5m --keep="man_made=pipeline" >$name.o5m
osmconvert $name.o5m -o=$name.pbf


cat <<ENDTEXT > custom.style
# OsmType  Tag          DataType     Flags

way        location        text         linear
way        layer        text         linear
way        diameter        text         linear
way        count        text         linear
way        pressure        text         linear
way        capacity        text         linear
way        substance        text         linear
way        usade        text         linear
way        name        text         linear
way        ref        text         linear


ENDTEXT



osm2pgsql --host 192.168.250.1 --database processing_osm_ch1 --create --latlong --style custom.style $name.pbf
wget --output-document=boundary.geojson http://datahub.nextgis.com/api/resource/57/geojson
ogr2ogr -progress  -f GPKG boundary.gpkg -progress -t_srs EPSG:4326 boundary.geojson

time ng_cutter -f "ESRI Shapefile" -lco ENCODING=UTF-8 $name.shp -progress -nlt LINESTRING -clipsrc boundary.gpkg "PG:host=192.168.250.1 dbname=processing_osm_ch1" "planet_osm_line"
zip $name.zip $name.shp $name.prj $name.dbf $name.shx  $name.cpg
rm $name.shp 
rm $name.prj 
rm $name.dbf 
rm $name.shx
rm $name.cpg
