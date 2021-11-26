#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import logging
from osgeo import gdal
from osgeo import osr
from pyproj import Proj, transform # reproject to 3857

#import sys
import stat
#sys.path.append("../core")
from qgis_project_substitute import substitute_project

import shutil

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class QGISTerminalRender:
    def reproject_4326_3857(self,x,y):
        inProj = Proj('epsg:4326')
        outProj = Proj('epsg:3857')
        xr,yr = transform(inProj,outProj,x,y)
        return xr,yr

    def get_layout_extent_vector_file(self,path):
        #return xml code for qgis layout page 
        
        assert os.path.isfile(path)
        ds = gdal.OpenEx(path,gdal.OF_READONLY)
        assert ds is not None
        layer = ds.GetLayer()
        assert layer is not None
        extent = layer.GetExtent()
  
        lx = extent[0]
        ly = extent[2]
        rx = extent[1]
        ry = extent[3]           
        bbox = '{lx},{ly},{rx},{ry}'.format(lx=lx,ly=ly,rx=rx,ry=ry)
        
        x1_3857,y1_3857 = self.reproject_4326_3857(ly,lx)
        x2_3857,y2_3857 = self.reproject_4326_3857(ry,rx)
                           
        layout_extent = '''<Extent xmin="{xmin}" ymin="{ymin}" xmax="{xmax}" ymax="{ymax}"/>'''.format(
        xmin=round(x1_3857),
        ymin=round(y1_3857),
        xmax=round(x2_3857),
        ymax=round(y2_3857),
         )
         
        return layout_extent
        
        
    def render(self):
    
        # Получить путь к слоям
        # Скопировать из архива слои в рабочий каталог
        # Расчитать экстент - сгенерировать geojson с охватом
        layout_extent = self.get_layout_extent_vector_file(os.path.join('data','highway.gpkg'))
        logger.info(layout_extent)
        assert layout_extent is not None
        WORKDIR = 'data'
        name = 'NAME'
        
        # Запись экстента в проект действует только для экспорта одиночной картинки.
        # В этом проекте по-другому: генерируется атлас, охват листа qgis берёт из слоя geojson, который заранее генерируется по охвату слоя.
        # Так упрощается отладка вёрстки страниц (это было актуально для OSMTram)
      
        # Рендеринг в картинку
        cmd = 'python3 pyqgis_client_atlas.py --project "{project}" --layout "1000x1000_atlas" --output "{filename}" '
        #TODO: пути должны быть абсолютные! С относительными путями не выходит
        cmd = cmd.format(project=os.path.join(WORKDIR,'manila.qgs'), filename=os.path.join(os.path.realpath(WORKDIR),''+name+'_kakava1000.png'))
        logger.info(cmd)
        os.system(cmd)

processor = QGISTerminalRender()
processor.render()
