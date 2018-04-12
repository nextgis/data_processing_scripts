Simple isodistance polygon generation in OSRM. Slow.

![demo](
https://github.com/nextgis/data_processing_scripts/raw/master/OSRM_distances/animation200.gif)

## Usade

```
#Подготовка файла домов
wget http://data.gis-lab.info/osm_dump/dump/latest/RU-MOW.osm.pbf
osm2pgsql --database processing_osm_ch1 --latlon RU-MOW.osm.pbf

python transport_atraction_zones.py -h

```
