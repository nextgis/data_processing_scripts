#!/usr/bin/env python
# -*- coding: utf-8 -*-

from osgeo import gdal
from osgeo import ogr
import os
import errno

import logging

import mergelines
processor = mergelines.Processor('/home/trolleway/ssdgis/mergeline/testdata/hi2.gpkg')

processor.mergelines()