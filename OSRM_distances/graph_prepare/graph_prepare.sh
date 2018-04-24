

filename='RU-MOS'
dbname='gis'
osrmbackend='~/osrm-backend'

wget --timestamping http://data.gis-lab.info/osm_dump/dump/latest/${filename}.osm.pbf
osmconvert $filename.osm.pbf -B=area.poly -o=background_clipped.o5m
osmfilter background_clipped.o5m --drop-author --keep="building=" --out-o5m >background-filtered.o5m
osmconvert background-filtered.o5m -o=background.pbf

osm2pgsql --database $dbname --latlon background.pbf
rm background-filtered.o5m







#Подготовка файла графа
filename='RU-MOS'
wget --timestamping http://data.gis-lab.info/osm_dump/dump/latest/${filename}.osm.pbf
osmconvert $filename.osm.pbf -B=area.poly -o=buildings_clipped.osm.pbf
#mv ".osm.pbf" "buildings_clipped.osm.pbf"

#далее запускаются штуки из каталога osrm-backend


filenamecl='background_clipped'

set -x
${osrmbackend}/build/osrm-extract $filenamecl.osm.pbf
${osrmbackend}/build/osrm-contract  $filenamecl.osrm
${osrmbackend}/build/osrm-routed --threads=6  $filenamecl.osrm
set +x

