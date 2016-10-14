#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Update and crop osm dump file for Moscow Oblast
# Author: Artem Svetlov <artem.svetlov@nextgis.com>



#if prevdump not exists - download CFO from geofabrik and crop to MosOblast
def updateDump():
    
    dump_url='http://planet.openstreetmap.org/pbf/planet-latest.osm.pbf'
    downloaded_dump='planet-latest.osm.pbf'
    work_dump='data.o5m'
    updated_dump='just_updated_dump.o5m'


    #frist run of program
    if exists(work_dump) = False:
        cmd='wget -O - '+dump_url ' | osmconvert - -o={dst_filename}.o5m'.format(src_filename=downloaded_dump, dst_filename=work_dump)
        print cmd
        os.system(cmd)

    #if prevdump dump exists - run osmupdate, it updating it to last hour state with MosOblast clipping, and save as currentdump
    os.system('osmupdate '+ work_dump + ' ' + updated_dump + '--daily --hourly ')
    
    #rename currentdump to prevdump
    os.remove(work_dump)
    os.rename(updated_dump, work_dump)

return 0
