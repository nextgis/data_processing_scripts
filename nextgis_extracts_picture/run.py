#!/usr/bin/python3
# -*- coding: utf8 -*-

import os
#os.system('Xvfb :1 -screen 0 800x600x24&')
#os.system('export DISPLAY=:1')

#https://gis.stackexchange.com/questions/362636/qgis-on-docker-container-could-not-connect-to-any-x-display
os.environ["QT_QPA_PLATFORM"] = "offscreen"

os.system('python3 pyqgis_client_atlas.py --project "extract/data.qgs" --layout "atlas_800x800" --output "spoon_RU-AST.png"')