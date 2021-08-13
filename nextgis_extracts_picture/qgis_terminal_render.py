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
