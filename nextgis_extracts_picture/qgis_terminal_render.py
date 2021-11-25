#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import logging
from osgeo import ogr
from osgeo import osr

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
  def render(self):
        substitute_project(
        src='../qgis_project_templates/manila.qgs.template.qgs',
        dst = WORKDIR+'/manila.qgs',
        layout_extent=layout_extent)
      
        cmd = 'python3 ../core/pyqgis_client_atlas.py --project "{WORKDIR}/manila.qgs" --layout "1000x1000_atlas" --output "{filename}" '
        cmd = cmd.format(WORKDIR=WORKDIR,filename=os.path.join(os.path.realpath(WORKDIR),''+name+'_kakava1000.png'))
        logger.info(cmd)
        os.system(cmd)
