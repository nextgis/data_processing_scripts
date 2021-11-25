#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import logging
from osgeo import ogr
from osgeo import osr
from pyproj import Proj, transform # reproject to 3857

#import sys
import stat
#sys.path.append("../core")
from qgis_project_substitute import substitute_project

import shutil
import zipfile

import config

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
        # Расчитать экстент
        layout_extent = self.get_layout_extent_vector_file(filename)
        
        # Записать файл проекта с экстентом в каталог
        substitute_project(
        src='../qgis_project_templates/manila.qgs.template.qgs',
        dst = WORKDIR+'/manila.qgs',
        layout_extent=layout_extent)
      
        # Рендеринг в карртинку
        cmd = 'python3 ../core/pyqgis_client_atlas.py --project "{WORKDIR}/manila.qgs" --layout "1000x1000_atlas" --output "{filename}" '
        cmd = cmd.format(WORKDIR=WORKDIR,filename=os.path.join(os.path.realpath(WORKDIR),''+name+'_kakava1000.png'))
        logger.info(cmd)
        os.system(cmd)
