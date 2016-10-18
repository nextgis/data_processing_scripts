#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Обработка выгрузок по США
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>


import process

# Все функции обработки записаны в файле process.py
# Для работы: запускается python main.py а в этом файле расскоментируются строки запуска отдельных функций


processor=process.Processor()
#processor.generate_filter_string() #Generate string with tags for osmfilter
#processor.osmimport('osm/north-america-latest')
#processor.needed_tags() #Инициализация, занесение нужных poi во временную таблицу
processor.grid_cycle() #генерирует в цикле сетку по одной строке, и пересекает точки




