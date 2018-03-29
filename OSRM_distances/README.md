Simple isodistance polygon generation in OSRM. Slow.

## Usade

```
#Подготовка файла домов
wget http://data.gis-lab.info/osm_dump/dump/latest/RU-MOW.osm.pbf
osm2pgsql --database processing_osm_ch1 --latlon RU-MOW.osm.pbf

python transport_atraction_zones.py -h

```