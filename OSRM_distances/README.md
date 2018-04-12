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

### Smooth polygon borders

Smooth borders in QGIS Processing using buffer_smooth.model

### Overlap polygons to touch polygons
```
python overlapped2touching.py -h
```


Run python transport_atraction_zones.py -h for more detailed description
