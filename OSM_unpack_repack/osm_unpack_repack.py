# -*- coding: utf-8 -*-
#unpack packages from data.nextgis.com
#Leave only needed layers
#Repack all back

import glob
import os
import shutil
import platform
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l','--layers',required=True,help='List of layers, comma separated')
parser.add_argument('-f','--format',choices=['shp','tab'],required=True,help='Data format')
parser.add_argument('-z','--zipformat',choices=['zip','7z'],required=True,help='Archive format')
args = parser.parse_args()

if platform.uname()[0] == 'Windows':
    path = '' #c:/tools/7-Zip/
    arcext = '.exe'
else:
    path = ''
    arcext = ''

zippath = path + '7z' + arcext
if not os.path.exists('res'): os.mkdir('res')
#layers = ['boundary-polygon','boundary-polygon-land','settlement-point','settlement-polygon']
layers = args.layers.split(',')
if args.format == 'shp':
    extensions = ['cpg','dbf','prj','shp','shx']
elif args.format == 'tab':
    extensions = ['dat','id','map','tab']

if args.zipformat == 'zip':
    arch = 'zip'
elif args.zipformat == '7z':
    arch = '7z'

    
for package in glob.glob('*.' + arch):
    print('Processing...' + package)
    dir = package.replace('.'+arch,'')
    if len(dir.split('-')) == 2:
        dirshort = dir.split('-')[0]
    else:
        dirshort = dir.split('-')[0] + '-' + dir.split('-')[1]
    
    os.mkdir(os.path.join('res',dirshort))
    cmd = zippath + ' x ' + package + ' -o' + os.path.join('tmp',dir)
    os.system(cmd)
    
    for layer in layers:
        for ext in extensions:
            f_in = os.path.join('tmp',dir,'data',layer + '.' + ext)
            f_out = os.path.join('res',dirshort,layer + '.' + ext)
            try:
                shutil.copy(f_in,f_out)
            except:
                pass