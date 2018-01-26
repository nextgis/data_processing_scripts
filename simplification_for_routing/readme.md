Merge two line layers with OSM data in pbf format to new pbf file for routing use in OSRM

Installation

```
git clone git://github.com/pnorman/ogr2osm.git
cd ogr2osm
git submodule update --init
cd ../

./run.py
```

```
Source files: 
30.geojson
36.geojson
source.osm.pbf

Output files:
graph.osm.pbf
```
