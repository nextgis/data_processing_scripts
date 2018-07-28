# -*- coding: utf-8 -*-
#unpack packages from data.nextgis.com
#Leave only needed layers
#Repack all back

import glob
import os
import shutil

zippath = 'c:\\tools\\7-Zip\\7z.exe'
os.mkdir('res')
layers = ['boundary-polygon','boundary-polygon-land','settlement-point','settlement-polygon']
extensions = ['cpg','dbf','prj','shp','shx']

for package in glob.glob('*.7z'):
    print('Processing...' + package)
    dir = package.replace('.7z','')
    dirshort = dir.split('-2018')[0]
    os.mkdir(os.path.join('res',dirshort))
    cmd = zippath + ' x ' + package + ' -o' + dir
    os.system(cmd)
    
    for layer in layers:
        for ext in extensions:
            f_in = os.path.join(dir,'data') + '\\' + layer + '.' + ext
            f_out = os.path.join('res',dirshort) + '\\' + layer + '.' + ext
            try:
                shutil.copy(f_in,f_out)
            except:
                pass