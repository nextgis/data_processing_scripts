

from osgeo import gdal, ogr, osr
import os

from zipfile import ZipFile

import time
startTime = time.time()

src_filename = 'ru-alos.geojson'
src_path = '/mnt/alpha/backups/data/dem-sources/alos2012dem'

#src_path = 'test'
unpack_dir = 'unpack'

if os.path.isfile('dem.tif'): os.unlink('dem.tif')
assert not os.path.isfile('dem.tif')

if os.path.isfile('mosaic.vrt'): os.unlink('mosaic.vrt')
assert not os.path.isfile('mosaic.vrt')

#прочесть файл
assert os.path.isfile(src_filename)
ds = gdal.OpenEx(src_filename)
driver = ds.GetDriver() 
layer = ds.GetLayer()

#взять охват
filenames_ok = list()
filenames_notfound = list()

tiles = layer.GetFeatureCount()
i=0
for feature in layer:
    i = i+1
    tile = feature.GetField('TILE')
    
    filename = os.path.join(src_path,tile)+'.zip'
    if os.path.isfile(filename):
        filenames_ok.append(filename)
    else:
        filenames_notfound.append(filename)


#распаковать 
i=0
for filename in filenames_ok:
    i=i+1
    print(str(i)+'/'+str(tiles))
    with ZipFile(filename, 'r') as zipObject:
       listOfFileNames = zipObject.namelist()
       for fileName in listOfFileNames:
           if 'DSM' in fileName and fileName.endswith('tif'):
               # Extract a single file from zip
               target = os.path.join(unpack_dir,os.path.basename(fileName))
               zipObject.extract(fileName, unpack_dir)
#добавить в VRT

cmd = 'find unpack -print | grep tif > list.txt'
os.system(cmd)
cmd = 'gdalbuildvrt -input_file_list list.txt mosaic.vrt'
os.system(cmd)

cmd = 'gdalwarp -r lanczos -t_srs EPSG:3857 -co TILED=yes -co COMPRESS=DEFLATE  mosaic.vrt dem.tif'
os.system(cmd)

executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))

with open("times.log", "a") as myfile:
    myfile.write('Execution time in seconds: ' + str(executionTime))
    
#создать из VRT маленький файл
#создать из VRT полный файл
