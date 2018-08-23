Merging lines by attributes into linestring.

# Demo

http://trolleway.nextgis.com/resource/2602

# Usage

See __main__.py for usage

* Input file must be Linestring geometry in any format. Convert it by
```
ogr2ogr -nlt Linestring -overwrite /home/trolleway/ssdgis/mergeline/testdata/hi2.gpkg /home/trolleway/ssdgis/mergeline/testdata/hi1.gpkg
```
* Output file must be geopackage.
* Only some fields are keep, some fields are dropped

# Known issues

* Некоторые линии дублируются, нужно что-то исправить в циклах
* Сейчас сравнение по одному захардкоденому полю NAME, а должно быть по списку полей
* Скрипт требует LINESTRING и генерирует Geopackage, нужно придумать где конвертировать в shapefile: тут или в другом месте
* Продумать логику, какие конкретно теги нужно оставлять, а какие выкидывать (SURFACE, REF, WIDTH) - это проблемы того скрипта который будет это вызывать
* Продумать логику, что делать с безымянными линиями. Если их просто не обрабатывать, а потом приклеить, то это даст многократное изменение скорости. Юзкейс: обработать выгрузку по всему Китаю