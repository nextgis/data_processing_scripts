

filename='RU-MOS'
wget --timestamping http://data.gis-lab.info/osm_dump/dump/latest/${filename}.osm.pbf
osmconvert $filename.osm.pbf -B=area.poly -o=background_clipped.o5m
osmfilter background_clipped.o5m --drop-author --keep="building=" --out-o5m >background-filtered.o5m
osmconvert background-filtered.o5m -o=background.pbf

osm2pgsql --database processing_osm_ch1 --latlon background.pbf
rm background-filtered.o5m







#Подготовка файла графа
filename='RU-MOS'
wget --timestamping http://data.gis-lab.info/osm_dump/dump/latest/${filename}.osm.pbf
osmconvert $filename.osm.pbf -B=area.poly -o=RU-MOS_clipped.osm.pbf
mv ".osm.pbf" "RU-MOS_clipped.osm.pbf"

#далее из каталога osrm-backend


filenamecl='RU-MOS_clipped'
osrm-extract /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/graph_prepare/$filenamecl.osm.pbf
osrm-contract /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/graph_prepare/$filenamecl.osrm
osrm-routed /home/trolleway/GIS/GIS/project98_isodistances/my6/data_processing_scripts/OSRM_distances/graph_prepare/$filenamecl.osrm

