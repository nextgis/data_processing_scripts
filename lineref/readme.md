align points with linear coordinates to linestring with geographic coordinates. Loop operations with ogrlineref utility

Имеется линия трассы (трубопровода), точечный слой пикетных отметок на трубе, точечный слой с координатами заданными пикетной отметкой на трубе.
1. Создаём вручную слой пикетных отметок (реперов) если его нет, считаем его пикетные отметки точными.
2. Скрипт запускает ogrlineref, из линии трассы и точек реперов делает слой с сегментами линий по 1000 метров, которые физически не обязательно 1000, а чуть растягиваются что бы притянуться к реперам.
3. Скрипт в цикле проходит по фичам из слоя измерений, вызывает ogrlineref и фичам в этом слое назначает координаты на трассе.


# Допущения
1. Слой с координатами заданными пикетной отметкой на трубе должен иметь какие-то точечные геометрии, в скрипте они заменяются.
2. В слое с трассой должна быть одна линейная фича.
3. Всё в метровой системе координат (EPSG:32367) (надо спросить у Димы, точно ли глюки были только из-за этого)

# Installation

```
1. Скопировать config.example.py в config.py 
2. Прописать в config.py доступ к базе и имена файлов

```

# Usage


```
python run.py


Открыть в QGIS слой PostGIS meashurements_geo, тот у которого поле геометрии назвается path_wkb_geometry.
```


