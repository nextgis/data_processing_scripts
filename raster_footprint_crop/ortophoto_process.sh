#!/bin/bash


# Some DEMs after Photoscan i found in 4326. Convert all to 32638. There should be convert only 4326
folder=dem
folder2=dem_rerojected
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
masks=masks.gpkg
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


#align dem heights
folder1=stage2
folderout=stage3
rm -r $folderout
mkdir $folderout

scene='2017-11-03-01'
delta=$(echo "155 - 121.77" | bc)
gdal_calc.py --calc "A+$delta" --format GTiff --type Float32 -A $folder1/$scene.tif --A_band 1 --outfile $folderout/$scene.tif
scene='2017-11-04-01'
delta=$(echo "156 - 125.45" | bc)
gdal_calc.py --calc "A+$delta" --format GTiff --type Float32 -A $folder1/$scene.tif --A_band 1 --outfile $folderout/$scene.tif

scene='2017-11-04-02'
delta=$(echo "139 - 146.62" | bc)
gdal_calc.py --calc "A+$delta" --format GTiff --type Float32 -A $folder1/$scene.tif --A_band 1 --outfile $folderout/$scene.tif

scene='2017-11-03-04'
delta=$(echo "87 - 65.18" | bc)
gdal_calc.py --calc "A+$delta" --format GTiff --type Float32 -A $folder1/$scene.tif --A_band 1 --outfile $folderout/$scene.tif

scene='2017-11-08-02'
delta=$(echo "306 - 243" | bc)
gdal_calc.py --calc "A+$delta" --format GTiff --type Float32 -A $folder1/$scene.tif --A_band 1 --outfile $folderout/$scene.tif

time python run.py --folder $folderout
gdal_translate  -q -of GTiff -outsize 30% 30%  stage3/stack/5.tif stage3/stack/stitched_relief.tif


mkdir tiles
cd tiles 
time gdal2tiles.py -z 1-17 ../stage3/stack/5.tif

#time gdal_translate -of GTiff  -outsize 20% 20% $folderout/stack/$scene.tif test.tif
#time gdal_translate -of GTiff  -outsize 20% 20% $folderout/$scene.tif test.tif
#time gdal_translate -of GTiff  -outsize 20% 20% $folder1/$scene.tif testo.tif


#stack raster merge to one 
time python run.py --folder $folder2

#preview
time gdal_translate -of GTiff  -outsize 20% 20% $folder2/stack/29.tif stacked.tif
