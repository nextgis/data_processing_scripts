#!/usr/bin/env python
# -*- coding: utf-8 -*-



postgresql_connection_string="host=localost user= dbname=gis password= "


#файл с реперами
src_repers_datasource_name = '../../../data/serv_UTM.shp'
#имя атрибута с пикетом в слое реперов
pos_field_name = 'Serv'
#промежуточный файл с сегментами
rsrc_parts_datasource_name = '../../../data/paths.shp'
#файл с точками заданными пикетами. Сейчас требуется чтоб это был слой с геометрией
measurements_layer_path = '../../../data/VTD2016_1.shp'
#название поля в measurements_layer_path
measurements_dist_field = 'dist_odom'
#файл с трассой. Реализовано для слоя с одной линией
src_line_datasource_name = '../../../data/Pipe_Line_UTM.shp'
#путь куда запишется слой, в котором точки будут перетянуты на линию
#points_on_lines_name = '../../../data/measurements_geo.shp'

#код epsg, в которой все слои
srid = 32643

#шаг разбивки
s = 1000