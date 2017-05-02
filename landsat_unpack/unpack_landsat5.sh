#/bin/sh

#Скрипт, который распаковывает сцены Landsat-5, делает 3-канальные tif, обрезает по geojson, генерит пирамиды, раскладывает по годам съёмки

#Все tar.gz лежат в одной папке. Распаковываем из них по одной нужной сцене
for zipped in *tar.gz; do tar -xzvf "$zipped" --wildcards --no-anchored '*B4.TIF'; done
for zipped in *tar.gz; do tar -xzvf "$zipped" --wildcards --no-anchored '*B3.TIF'; done
for zipped in *tar.gz; do tar -xzvf "$zipped" --wildcards --no-anchored '*B2.TIF'; done


#Генерация файла со списком сцен
ls *tar.gz | sed 's/_T1.*//' > scenes.list

#Создание vrt с тремя каналами
while read s; do  gdalbuildvrt -separate $s.vrt ${s}_T1_B4.TIF ${s}_T1_B3.TIF ${s}_T1_B2.TIF; done < scenes.list

#Обрезка по полигональному geojson. Он должен быть в той же CRS, что и космоснимки, у меня - EPSG:32650
while read s; do  gdalwarp -dstnodata 0 -co COMPRESS=JPEG -co JPEG_QUALITY=95  -cutline boudary_32650.geojson  $s.vrt ../$s.tif ; done < scenes.list

#К каждому tiff прикладываем одинаковую копию qml с названием сцены - там настройки цветов и констрастности, чтоб в qgis было лучше видно
while read s; do  cp default.qml ../$s.qml ; done < scenes.list

#Генерация пирамид, что бы было быстрее скроллить в qgis
while read s; do  gdaladdo -r CUBIC --config COMPRESS_OVERVIEW JPEG -ro  ../$s.tif 2 4 8 16 32 64 ; done < scenes.list

cd ../
mkdir 2000
mkdir 2001
mkdir 2002
mkdir 2003
mkdir 2004
mkdir 2005
mkdir 2006
mkdir 2007
mkdir 2008
mkdir 2009
mkdir 2010
mkdir 2011
mkdir 2012
mkdir 2013
mkdir 2014


mv *_2001????_* 2001
mv *_2002????_* 2002
mv *_2003????_* 2003
mv *_2004????_* 2004
mv *_2005????_* 2005
mv *_2006????_* 2006
mv *_2007????_* 2007
mv *_2008????_* 2008
mv *_2009????_* 2009
mv *_2010????_* 2010
mv *_2011????_* 2011
mv *_2012????_* 2012
mv *_2013????_* 2013
mv *_2014????_* 2014
