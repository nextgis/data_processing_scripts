# boundary_polygon_up

open boundary-polygon.shp from nextgis OSM to SHP extracts, for each feature add 3 attributes with names of upper administrative objects.

Открывает  boundary-polygon.shp из выгрузкок OSM в SHP, для каждого полигона добавляет 3 атрибута с названиями вышестоящих административных единиц.

![alt text](https://github.com/nextgis/data_processing_scripts/raw/master/boundary_polygon_up/sample.png "Result in QGIS")


# Usage

With overwrite
```
python boundary_polygon_up.py -s ../../test/data/boundary-polygon.shp
```

With create new files
```
python boundary_polygon_up.py -s ../../test/data/boundary-polygon.shp -d ../../test/result.shp
```
