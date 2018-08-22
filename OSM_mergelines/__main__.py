#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osgeo import gdal
from osgeo import ogr
import os
import errno

import logging

import mergelines
processor = mergelines.Processor('/home/trolleway/ssdgis/mergeline/testdata/hi2.gpkg') #only LINESTRING
processor.mergelines(output_filename='/home/trolleway/ssdgis/mergeline/testdata/result.gpkg',DifferentFeaturesList=('NAME','HIGHWAY')) #only gpkg


'''
ogr2ogr -nlt Linestring /home/trolleway/ssdgis/mergeline/testdata/hi2.gpkg /home/trolleway/ssdgis/mergeline/testdata/hi1.gpkg
'''