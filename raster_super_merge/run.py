#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Raster super merge
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016-2018, NextGIS <info@nextgis.com>


import os
import argparse

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
                          argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='merge rasters smart way',
                                     formatter_class=PrettyFormatter)

    parser.add_argument('--folder',
                        help='Take all tiffs from this folder',
                        default=os.getcwd())
    parser.add_argument('--quality',
                        help='JPEG quality for final step',
                        default=75)
    parser.epilog = \
        ''' '''
    return parser


parser = argparser_prepare()
args = parser.parse_args()





compress_settings = '-co COMPRESS=JPEG -co JPEG_QUALITY=75'
compress_settings = ''

files = list()


dirpath = args.folder

'''
        listfiles=['2017-11-06','2017-11-07','2017-11-08'] #фильтр по именам файлов
        if any(word in file for word in listfiles):
'''
# generate filelist from dir

for file in sorted(os.listdir(dirpath)):
    if (file.endswith(".tif")) or (file.endswith(".tiff")):
        files.append(file)


# output dir is same as input
stack_dir = os.path.join(dirpath,'stack')
if not os.path.exists(stack_dir):
    os.makedirs(stack_dir)

i=0
# for each raster
for file in files:
    i=i+1
    if i == 1:
        #копирование первого растра
        #на всякий случай без shutil чтоб заработало на винде
        file_result = os.path.join(stack_dir,str(i))+'.tif'
        file_current = os.path.join(dirpath,file)
        cmd = 'gdal_translate -lco SPARSE_OK=TRUE -q -of GTiff {compress_settings}  {file_current} {file_result} '.format(file_result=file_result, file_current=file_current, compress_settings=compress_settings)
        print cmd
        os.system(cmd)
    #print file
    if i > 1:
        file_result = os.path.join(stack_dir,str(i))+'.tif'
        file_prev = os.path.join(stack_dir,str(i-1))+'.tif'
        file_current = os.path.join(dirpath,file)
        cmd = 'gdal_merge.py  -lco SPARSE_OK=TRUE -q -of GTiff {compress_settings} -v -o {file_result} {file_prev} {file_current}'.format(file_result = file_result, file_prev=file_prev, file_current=file_current, compress_settings=compress_settings)
        
        print cmd
        os.system(cmd)
# merge prev raster with next and save to stack dir

#result raster
print 'final'
file_current = file_result
file_result = os.path.join(stack_dir,'supermerge')+'.tif'
cmd = 'gdal_translate  -q -of GTiff -co COMPRESS=JPEG -co JPEG_QUALITY={quality}  {file_current} {file_result} '.format(file_result=file_result, file_current=file_current, quality=str(args.quality))
print cmd
os.system(cmd)
