Merge two line layers with OSM data in pbf format to new pbf file for routing use in OSRM

# Installation

```
1. Скопировать config.example.py в config.py 
2. Прописать в config.py доступ к базе
3. pip install -r requirements.txt
```

# Usage


Прописать в файле run.py ссылки на файлы.

```
python run.py


Открыть в QGIS слой PostGIS meashurements_geo, тот у которого поле геометрии назвается path_wkb_geometry.
```


