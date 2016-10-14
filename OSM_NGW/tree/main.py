#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Выгрузка слоя из OSM в NGW
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>


import process

# Все функции обработки записаны в файле process.py
# Для работы: запускается python main.py а в этом файле расскоментируются строки запуска отдельных функций


#Этот скрипт запускается из верхней папки

processor=process.Processor()
processor.osmimport('data')
processor.postgis2geojson('planet_osm_point')
os.system('python update_ngw_from_geojson.py  --ngw_url '+processor.config.ngw_url+' --ngw_resource_id '+processor.config.ngw_res_id+' --ngw_login '+processor.config.ngw_login+' --ngw_password '+processor.config.ngw_password+' --check_field road_id --filename routes_with_refs.geojson')




