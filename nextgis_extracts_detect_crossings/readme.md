# detect_crossings
open highway-line.shp from nextgis OSM to SHP extracts, generate point layer with crossings, and count of road on each crossing

![alt text](https://github.com/nextgis/data_processing_scripts/raw/master/nextgis_extracts_detect_crossings/sample.png "Result in QGIS")


# Usage


```
python detect_crossings.py -s ../../test/data/boundary-polygon.shp -d ../../test/result.shp
```

With custom highway filter
```
python detect_crossings.py -s ../../test/data/boundary-polygon.shp -d ../../test/result.shp
time python detect_crossings.py -s ../../test/data/highway-line.shp -d crossings.shp -f "HIGHWAY IN ('primary') "
time python detect_crossings.py -s ../../test/data/highway-line.shp -d crossings.shp -f "HIGHWAY IN ('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link','unclassified','residential')"
```
