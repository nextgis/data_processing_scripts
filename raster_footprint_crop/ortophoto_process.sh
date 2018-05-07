#!/bin/bash

masks=dagestan2017_scene3/scene3_masks.gpkg

# Some DEMs after Photoscan i found in 4326. Convert all to 32638. There should be convert only 4326
folder=imagery
folder2=imagery_reprojected
rm -r $folder2
mkdir $folder2
FILES=$folder/*.tif
for f in $FILES
do
	scene=$(basename "$f" .tif)
	echo "Processing $scene "
	gdalwarp -q -ot Float32  -t_srs EPSG:32638 -r cubicspline -of GTiff -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 -wo OPTIMIZE_SIZE=TRUE $folder/$scene.tif $folder2/$scene.tif
done



#Walk by folder with rasters, clip by vector feature from masks vector file

folder=dem_rerojected
folder2=stage2
rm -r $folder2
mkdir $folder2
FILES=$folder/*.tif
for f in $FILES
do
	scene=$(basename "$f" .tif)
 	echo "Processing $scene "
 	gdalwarp -q -cutline $masks -cl masks -cwhere scene=\'$scene\' -crop_to_cutline -dstalpha $folder/$scene.tif $folder2/$scene.tif

done



#time gdal_translate -of GTiff  -outsize 20% 20% $folderout/stack/$scene.tif test.tif
#time gdal_translate -of GTiff  -outsize 20% 20% $folderout/$scene.tif test.tif
#time gdal_translate -of GTiff  -outsize 20% 20% $folder1/$scene.tif testo.tif


#stack raster merge to one 
time python run.py --folder $folder2

#preview
time gdal_translate -of GTiff  -outsize 20% 20% $folder2/stack/29.tif stacked.tif
