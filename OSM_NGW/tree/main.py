#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Выгрузка слоя из OSM в NGW
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>


import process
import os


# Все функции обработки записаны в файле process.py
# Для работы: запускается python main.py а в этом файле расскоментируются строки запуска отдельных функций


#Этот скрипт запускается из верхней папки

processor=process.Processor()
processor.osmimport('data')
processor.postgis2geojson('planet_osm_point')
os.system('python update_ngw_from_geojson.py  --ngw_url '+processor.ngw_url+' --ngw_resource_id '+processor.ngw_res_id+' --ngw_login '+processor.ngw_login+' --ngw_password '+processor.ngw_password+' --check_field osm_id --filename tree/planet_osm_point.geojson')




