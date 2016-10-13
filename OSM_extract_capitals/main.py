#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Выгрузка точек столичных НП из OSM
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>


import process

# Все функции обработки записаны в файле process.py
# Для работы: запускается python main.py а в этом файле расскоментируются строки запуска отдельных функций


processor=process.Processor()
processor.osmimport('osm/planet-latest')




