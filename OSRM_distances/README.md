Simple isodistance polygon generation in OSRM. Slow.

![demo](
https://github.com/nextgis/data_processing_scripts/raw/master/OSRM_distances/animation200.gif)

## Usade

### Create Postgis table with buildig polygons

see graph_prepar/graph_prepare.sh

### Prepare OSRM graph

see graph_prepar/graph_prepare.sh

### Calc isodistances polygon
```
python transport_atraction_zones.py -h
```

Create polygons for all points in point layer

Settings:

```
--overlap touching (default)
```
Генерирует соприкасающиеся полигоны, которые показывают, от какого старта ближе ехать до какой-либо точки. Потом следует сделать постобработку overlapped2touching.py
```
--overlap overlapped: 
```
Генерирует накладывающиеся полигоны, которые показывают все точки на заданом расстоянии от каждого старта.

![demo](
https://raw.githubusercontent.com/nextgis/data_processing_scripts/master/OSRM_distances/overlapped.png)

### Smooth polygon borders

```
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
```

![demo](
https://raw.githubusercontent.com/nextgis/data_processing_scripts/master/OSRM_distances/isodistances_smooth.png)

### Touch polygons postprocessing when --overlap touching
```
python overlapped2touching.py -h
```
![demo](
https://raw.githubusercontent.com/nextgis/data_processing_scripts/master/OSRM_distances/isodistances_overlap2touched.png)

#### When polygons needed with different distances 

```
#!/bin/bash

set -x

dist='2000'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='2500'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='3000'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='3500'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='4000'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='4500'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='5000'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='5500'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg
dist='6000'
rm step3_overlap/overlapped$dist.gpkg
time python /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/overlapped2touching.py --pg_conn "dbname=processing_osm_ch1" \
--input step2_qgis/simpl$dist.gpkg --output step3_overlap/$dist.gpkg



#ogrmerge work at my machine only with vrt
#vrt render in qgis slowly
ogrmerge.py -f VRT -single -o merged.vrt step3_overlap/*.gpkg -src_layer_field_name val
rm  merged.gpkg
ogr2ogr -f "gpkg" merged.gpkg merged.vrt -sql "SELECT  left(val,4)/1000 AS distance,shop_id  "

```

### Create gif animation
```
ffmpeg -f image2 -pattern_type glob -i '*.png' animated.gif
# -pattern_type glob not avaible under Windows
```


Run python transport_atraction_zones.py -h for more detailed description
