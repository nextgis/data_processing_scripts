#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: osm-extracts
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2022, NextGIS <info@nextgis.com>

'''
Convert ALOS DEM for NextGIS.com 
- filter by geojson file
- merge
- convert for optimal format
- write benchmark file

python3 dem4country.py caucaus.geojson /mnt/alpha/backups/data/dem-sources/alos2012dem ./caucasus.tif
python3 dem4country.py -cutline boundary4326.gpkg caucaus.geojson /mnt/alpha/backups/data/dem-sources/alos2012dem ./caucasus.tif
'''

import argparse

from osgeo import gdal, ogr, osr
import os

from zipfile import ZipFile

import time

def alos4ngw(grid, src_path, result_path, te=None, te_srs=None,clipsrc=None):
    startTime = time.time()
    assert te is None or ',' not in te
    if te is None: 
        te = '' 
    else: 
        te='-te '+te
    if te_srs is None: 
        te_srs = '' 
    else: 
        te_srs='-te_srs '+te_srs
    
    assert os.path.isfile(grid), 'invalid grid path: '+grid
    assert os.path.isdir(src_path), 'invalid path: '+src_path
    assert os.path.isdir(os.path.dirname(result_path)) or result_path == '', 'invalid result path: '+result_path

    unpack_dir = 'unpack'

    if os.path.isfile('dem.tif'): os.unlink('dem.tif')
    assert not os.path.isfile('dem.tif')

    if os.path.isfile('mosaic.vrt'): os.unlink('mosaic.vrt')
    assert not os.path.isfile('mosaic.vrt')

    #read grid geojson
    assert os.path.isfile(grid)
    ds = gdal.OpenEx(grid)
    driver = ds.GetDriver() 
    layer = ds.GetLayer()


    #create list of ALOS tiles exists on drive
    filenames_ok = list()
    filenames_notfound = list()

    tiles = layer.GetFeatureCount()
    i=0
    cmd = 'rm -rf list.txt'
    os.system(cmd)
    for feature in layer:
        i = i+1
        tile = feature.GetField('TILE')
        
        filename = os.path.join(src_path,tile)+'.zip'
        if os.path.isfile(filename):
            filenames_ok.append(filename)
        else:
            filenames_notfound.append(filename)


    #Extract ALOS scenes, extract *DSM*.tif
    cmd = 'rm -rf unpack/*'
    os.system(cmd)
    print('extracting...')
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
    
    #make VRT with all extracted rasters
    cmd = 'find unpack -print | grep tif > list.txt'
    os.system(cmd)
    print('build VRT')
    cmd = 'gdalbuildvrt -input_file_list list.txt mosaic.vrt'
    os.system(cmd)

    print('Reprojecting preview 4000x4000 px ...')
    #To prevent blocky pattern, resampling in reproject must be one of cubicspline,cubic,bilinear.  Also you should set resampling in QML in QGIS.
    preview_filename = os.path.splitext(result_path)[0] + '_preview'+os.path.splitext(result_path)[1]
    if clipsrc is not None:
        clip_command = f'-cutline {clipsrc}  -crop_to_cutline -dstalpha '
    else:
        clip_command = ''
    cmd = 'gdalwarp -r cubicspline -multi -overwrite -ts 4000 4000 -t_srs EPSG:3857  -ot Int16 {te} {te_srs} {clip_command} -co TILED=yes -co COMPRESS=DEFLATE  -co BIGTIFF=YES  mosaic.vrt '.format(te=te,te_srs=te_srs,clip_command=clip_command)+preview_filename
    os.system(cmd)
    
    print('Reprojecting...')    
    cmd = 'gdalwarp -r cubicspline -multi -overwrite -t_srs EPSG:3857  -ot Int16  {te} {te_srs} {clip_command} -co TILED=yes -co COMPRESS=DEFLATE  -co BIGTIFF=YES  mosaic.vrt '.format(te=te,te_srs=te_srs,clip_command=clip_command)+result_path
    os.system(cmd)
    #if source raster is UInt16, a hillshade with splines will not draw good, explicit convert to Int16

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))

    with open("times.log", "a") as myfile: 
        myfile.write('Execution time in seconds: ' + str(executionTime))


if __name__== "__main__":
    parser = argparse.ArgumentParser(description='Convert ALOS DEM files to single GeoTIFF file for NextGIS WEB. Do select by geojson, merge, reproject, set special resampling method, raster compress algoritm')
    parser.add_argument('grid', help='Path to grid geojson file', type=str)
    parser.add_argument('src_path', help='Path to directory with ALOS DSM tiles', type=str)
    parser.add_argument('-te','--bbox', dest='te', help='gdalwarp te bbox', required=False, type=str)
    parser.add_argument('-te_srs','--bbox_srs', dest='te_srs', help='gdalwarp bbox SRC', required=False, type=str)
    parser.add_argument('-cutline', dest='cutline', help='clip by mask using vector file', required=False, type=str)
    parser.add_argument('result_path', help='Path to result TIF file', default='dem.tif', type=str)
    
    args = parser.parse_args()
    alos4ngw(grid=args.grid, src_path=args.src_path, result_path=args.result_path, te=args.te, te_srs=args.te_srs, clipsrc=args.cutline)
