# -*- coding: utf-8 -*-
'''


Usage: manualstart.py regions
'''
from __future__ import unicode_literals

import os
import shutil



import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Выкачивает с гис-лаба pbf по региону, конвертирует его в пачку шейпов, запихивает в проект.',
            formatter_class=PrettyFormatter)
    parser.add_argument('region', type=str, 
                           help='Region code. Listed at http://data.nextgis.com/osmshp/')



    parser.epilog = \
        '''Samples: 

%(prog)s RU-TY 
''' \
        % {'prog': parser.prog}
    return parser

parser = argparser_prepare()
args = parser.parse_args()


import shlex
#from __future__ import print_function # Only Python 2.x
import subprocess

def execute(cmd):
    #execute system command and return every string of it output just as it comes
    popen = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, b""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)



def truncate_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def pbf2shplayer(layerref,OSM_CONFIG_FILE,nlt,where,export_filename,temp_filename,config_content,sql):


    if not os.path.exists(pbf2shpfolder):
        os.makedirs(pbf2shpfolder)

    ogr_config = open(OSM_CONFIG_FILE, 'w')
    ogr_config.write(config_content)
    ogr_config.close()


    print "Запуск ogr2ogr"
    cmd = 'ogr2ogr -overwrite --config OSM_CONFIG_FILE {OSM_CONFIG_FILE} -nlt {nlt} \
    -lco ENCODING=UTF-8 -where "{where}" \
    -skipfailures -f "ESRI Shapefile" '+os.path.join(pbf2shpfolder) + ' ' + pbf_filename
    cmd = cmd.format(OSM_CONFIG_FILE=OSM_CONFIG_FILE, where=where,nlt=nlt)
    for response in execute(cmd):
        #print(response)
        pass

    print 'это был запуск'
    print cmd 
    print


    #Если не задан параметр sql, то используем where
    #Если задан параметр sql, то составляем sql-запрос для переименования полей
    print "Move shapefile through ogr2ogr" 
    #TODO: переносить и переименовывать все файлы по маске используя os

    cmd = 'ogr2ogr -overwrite  \
    -lco ENCODING=UTF-8  \
    -skipfailures  -where "{where}" -f "ESRI Shapefile" {export_filename}.shp {temp_filename}.shp'
    cmd = cmd.format(export_filename=export_filename,temp_filename=temp_filename, where=where,sql=sql)
    for response in execute(cmd):
        print(response)

    print
    print 'truncate temporary shapefiles folder'
    #truncate_folder(pbf2shpfolder)
    shutil.rmtree(pbf2shpfolder)
    print 'Processed layer ' + layerref

region = args.region

#имя файла который сейчас скачивается. тут можно приделать хеш, для возможности паралельного запуска
pbf_filename = 'current.pbf'
#имя промежуточной папки. Из osm туда сваливаются 5 шейпов всех типов геометрий, потом из неё вытаскивается один, и кладётся в папку с проектом кугиса
pbf2shpfolder = 'tmp'
#имя папки, куда будут сваливаться шейпы
exportfolder = os.path.join('newlayers','data')

#выкачивать ли дамп?
is_download = False

if is_download:
    print "Выкачиваю pbf"
    cmd = 'wget -O ' + pbf_filename +  ' -N http://data.gis-lab.info/osm_dump/dump/latest/RU-KHA.osm.pbf'
    print cmd

    for response in execute(cmd):
        print(response)



#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='boundary-polygon'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'MULTIPOLYGON'
where = "admin_level is not null"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content='''
closed_ways_are_polygons=admin_level

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[multipolygons]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no
osm_way_id=no


# keys to report as OGR fields
attributes=name,admin_level,name:ru,name:en
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''
sql='''SELECT name,admin_level AS admin_lvl,name_ru,name_en FROM multipolygons'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content,sql=sql)

quit()

#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='settlement-point'
#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'POINT'
where = "place in ('town','city','village','hamlet','locality')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'points') 
config_content = '''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[points]
# common attributes
# note: for multipolygons, osm_id=yes instantiates a osm_id field for the id of relations
# and a osm_way_id field for the id of closed ways. Both fields are exclusively set.
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,name:en,name:ru,place,addr:country,addr:region,addr:district,addr:postcode,population
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)



#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='settlement-polygon'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'MULTIPOLYGON'
where = "place in ('town','city','village','hamlet','locality')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content = '''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[multipolygons]
# common attributes
# note: for multipolygons, osm_id=yes instantiates a osm_id field for the id of relations
# and a osm_way_id field for the id of closed ways. Both fields are exclusively set.
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,name:en,name:ru,place,addr:country,addr:region,addr:district,addr:postcode,population
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''
pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='highway-line'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'LINESTRING'
where = "highway IN ('motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary',    'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link',    'residential', 'unclassified', 'road', 'living_street', 'service', 'track',     'pedestrian', 'footway', 'path', 'steps', 'bridleway', 'construction',    'cycleway', 'proposed', 'raceway')"
    #путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'lines') 
config_content='''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[lines]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,ref,highway,oneway,bridge,tunnel,maxspeed,lanes,width,surface
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)

#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='water-line'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'LINESTRING'
where = "waterway IN ('river', 'stream', 'canal', 'drain')"
    #путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'lines') 
config_content='''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[lines]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,waterway
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='water-polygon'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'MULTIPOLYGON'
where = "natural IN ('water', 'wetland') OR waterway = 'riverbank'"
    #путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content='''
closed_ways_are_polygons=riverbank

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[multipolygons]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,natural,waterway,wetland
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)



#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='railway-line'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'LINESTRING'
where = "railway IN ('rail', 'tram', 'light_rail', 'abandoned', 'disused',      'subway', 'preserved', 'construction', 'narrow_gauge', 'service',      'siding', 'spur', 'monorail', 'monoroail', 'proposed')"
          #путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'lines') 
config_content='''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[lines]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,railway,gauge,service,bridge,tunnel
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='railway-station-point'
#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'POINT'
where = "railway IN ('station', 'halt', 'tram_stop')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'points') 
config_content = '''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[points]
# common attributes
# note: for multipolygons, osm_id=yes instantiates a osm_id field for the id of relations
# and a osm_way_id field for the id of closed ways. Both fields are exclusively set.
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,name:en,name:ru,railway
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)



#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='vegetation-polygon'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'MULTIPOLYGON'
where = "natural IN ('wood', 'scrub', 'heath') OR landuse IN ('forest')"
    #путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content='''
closed_ways_are_polygons=riverbank

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[multipolygons]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,natural,landuse,wood
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='landuse-polygon'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'MULTIPOLYGON'
where = " landuse IS NOT NULL AND NOT landuse IN ('forest')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content='''
closed_ways_are_polygons=landuse

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[multipolygons]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no
osm_way_id=no


# keys to report as OGR fields
attributes=name,landuse,residential
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)

#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='building-point'
#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'POINT'
where = "building IS NOT NULL AND NOT building IN ('no', 'entrance')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'points') 
config_content = '''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[points]
# common attributes
# note: for multipolygons, osm_id=yes instantiates a osm_id field for the id of relations
# and a osm_way_id field for the id of closed ways. Both fields are exclusively set.
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=building,name,addr:street,addr:suburb,addr:housenumber,building:levels
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='building-polygon'
#Конфиг ogr для слоя
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип, хотя он вроде не используется
nlt = 'MULTIPOLYGON'
where = "building IS NOT NULL AND NOT building IN ('no', 'entrance')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content='''
closed_ways_are_polygons=building

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

[multipolygons]
# common attributes
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no
osm_way_id=no


# keys to report as OGR fields
attributes=building,name,addr:street,addr:suburb,addr:housenumber,building:levels
# keys that should NOT be reported in the "other_tags" field
ignore=created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
'''


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='poi-point'

#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'POINT'
where = "man_made IS NOT NULL OR leisure IS NOT NULL OR amenity IS NOT NULL OR office IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL OR sport IS NOT NULL"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'points') 
config_content = '''
closed_ways_are_polygons=place

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[points]
# common attributes
# note: for multipolygons, osm_id=yes instantiates a osm_id field for the id of relations
# and a osm_way_id field for the id of closed ways. Both fields are exclusively set.
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,name:en,name:ru,man_made,leisure,amenity,sport,office,shop,tourism
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)



#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='poi-polygon'

#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'MULTIPOLYGON'
where = "man_made IS NOT NULL OR leisure IS NOT NULL OR amenity IS NOT NULL OR office IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL OR sport IS NOT NULL"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content = '''
closed_ways_are_polygons=man_made,leisure,amenity,office,shop,tourism,sport

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[multipolygons]
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,name:en,name:ru,man_made,leisure,amenity,sport,office,shop,tourism
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)



#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='nature_reserve-polygon'

#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'MULTIPOLYGON'
where = "leisure = 'nature_reserve' OR boundary = 'national_park' OR boundary = 'protected_area'"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content = '''
closed_ways_are_polygons=leisure=nature_reserve,boundary=national_park,boundary=protected_area

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[multipolygons]
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,name:en,name:ru,leisure,boundary
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='surface-polygon'

#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'MULTIPOLYGON'
where = "natural IN ('beach', 'sand', 'fell', 'grassland', 'heath', 'scree','scrub')"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content = '''
closed_ways_are_polygons=natural=beach,natural=sand,natural=fell,natural=grassland,natural=heath,natural=scree,natural=scrub

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[multipolygons]
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=natural
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)


#---------------------------------------------------------------------------------------------------------------------------------

#код слоя
layerref='railway-platform-polygon'

#Путь во временной папке, куда запишется конфиг драйвера osm
OSM_CONFIG_FILE = os.path.join('layerscfg',layerref)+'.ini'
#тип геометрии ogr
nlt = 'MULTIPOLYGON'
where = "railway = 'platform'"
#путь+базовая часть имени шейпфайла, как он будет класться в папку с проектом qgis 
export_filename=os.path.join(exportfolder,layerref)
#путь+базовая часть имени шейпфайла, как он получается при конвертации из pbf
temp_filename = os.path.join(pbf2shpfolder,'multipolygons') 
config_content = '''
closed_ways_are_polygons=railway

# comment to avoid laundering of keys ( ':' turned into '_' )
attribute_name_laundering=yes

# uncomment to report all nodes, including the ones without any (significant) tag
#report_all_nodes=yes

# uncomment to report all ways, including the ones without any (significant) tag
#report_all_ways=yes



[multipolygons]
osm_id=yes
osm_version=no
osm_timestamp=no
osm_uid=no
osm_user=no
osm_changeset=no

# keys to report as OGR fields
attributes=name,railway,ref
# keys that should NOT be reported in the "other_tags" field
ignore=area,created_by,converted_by,source,time,ele,note,openGeoDB:,fixme,FIXME
# uncomment to avoid creation of "other_tags" field
other_tags=no
# uncomment to create "all_tags" field. "all_tags" and "other_tags" are exclusive
#all_tags=yes
'''

pbf2shplayer(layerref=layerref,OSM_CONFIG_FILE=OSM_CONFIG_FILE,nlt=nlt,where=where,export_filename=export_filename,temp_filename=temp_filename,config_content=config_content)



#
quit()
