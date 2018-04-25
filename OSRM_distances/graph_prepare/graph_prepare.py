# -*- coding: utf-8 -*-

import subprocess
import shlex
import os

filename = 'RU-MOS'
dbname = 'gis'
osrmbackend = '/home/trolleway/osrm-backend'
threads = 6

#download and filtering pbf
subprocess.call(shlex.split('wget --timestamping http://data.gis-lab.info/osm_dump/dump/latest/'+filename+'.osm.pbf'))
subprocess.call(shlex.split('osmconvert '+ filename+'.osm.pbf -B=area.poly -o=background_clipped.o5m'))
subprocess.call(shlex.split('osmfilter background_clipped.o5m --drop-author --keep="building=" --out-o5m >background-filtered.o5m'))
subprocess.call(shlex.split('osmconvert background-filtered.o5m -o=background.pbf'))
subprocess.call(shlex.split('osm2pgsql --database '+dbname +' --latlon background.pbf'))
subprocess.call(shlex.split('rm background-filtered.o5m'))
subprocess.call(shlex.split('wget --timestamping http://data.gis-lab.info/osm_dump/dump/latest/'+filename+'.osm.pbf'))
subprocess.call(['osmconvert',filename+'.osm.pbf','-B=area.poly','-o=buildings_clipped.osm.pbf']) #составить это из строки не получилось из-за непонятного поведения subprocess

#prepare graph for OSRM
filenamecl='buildings_clipped'
subprocess.call(shlex.split(os.path.join(osrmbackend,'build','osrm-extract')+' '+filenamecl+'.osm.pbf --profile '+os.path.join(osrmbackend,'profiles','car.lua') ))
subprocess.call(shlex.split(os.path.join(osrmbackend,'build','osrm-contract')+' '+filenamecl+'.osrm'))

#start OSRM server
subprocess.call(shlex.split(os.path.join(osrmbackend,'build','osrm-routed')+' --threads=' + str(threads) +'  '+filenamecl+'.osrm'))
