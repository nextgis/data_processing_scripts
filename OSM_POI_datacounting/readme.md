# Как заниматься геомаркетинговым анализом в PostGIS

Задача: посмотреть сколько в РФ магазинов одной сети, и посмотреть, у каких из них какие нужные теги введены.

### Соглашения в тексте

* БД называется gis, некоторые утилиты так делают по умолчанию
* Поле геометрии называтеся wkb_geometry
* СК 4326
* Кодировка UTF8
* дампы имеют расширение .osm.pbf, так их видит josm.
* Импортировать базу всё равно в чём - osm2pgsql, osmosis, imposm. Но эти утилиты дают разные схемы. Я использую osm2pgsql.

# Инструкция.
Поднять PostgreSQL и расширение к нему PostGIS. Воспользуйтесь пакетным менеджером вашей ОС или docker-compose.

Создайте юзера в postgresql, базу данных "gis", в ней create extension PostGIS. Это проще всего делать в PGAdminIII.

Поставить пакеты osm2pgsql, osmctools, aria2c. Поставить PGadmin, версия 3 мне больше нравится по UX, чем версия 4.

Импортировать дамп РФ долго, но его можно быстро отфильтровать, выкинув всё кроме магазинов, а потом импортировать.


## Фильтрация дампа в pbf по тегам
```
sudo apt-get install aria2c osmctools osm2pgsql 
aria2c http://download.geofabrik.de/russia/kaliningrad-latest.osm.pbf  #многопоточная скачка файла
$dump = 'russia-latest' #это переменная с названием файла

osmconvert $dump.osm.pbf -o=$dump.o5m
osmfilter $dump.o5m --keep="amenity,shop" --out-o5m >$dump-filtered.o5m
osmconvert $dump-filtered.o5m -o=$dump-filtered.osm.pbf

```

## Загрузка дампа в PostGIS

```
osm2pgsql --create --latlong --database gis $dump-filtered.osm.pbf
```
Тут наверно будет спрашивать логин и пароль, с автоматизацией их ввода нужны какие-то танцы с бубном, проще вводить с клавиатуры вручную. 
Эта комманда создаст в базе gis разные таблицы с геометрией. Конкретные названия и структура таблиц зависит от утилиты.

## Загрузка дампа в PostGIS теперь уже с нужными тегами.

osm2pgsql создаёт поля в таблице только для некоторых тегов OSM, почти всегда некоторые нужные теги пропускаются. Поэтому есть 2 варианта:

1. Указать в конфиге, чтоб теги писались в одно поле типа hstore. Я это не использую, потому что так плохо видно, и для hstore какие-то операторы странные, из крючков.
2. Прописать в конфиге какие теги нужны. Тогда они запишутся как столбцы таблицы. 

Для этого: 

Найти в своей ОС файл конфига, который поставился вместе с osm2pgsql. Это типа /usr/share/osm2pgsql/default.style

Скопировать его в рабочий каталог, дописать там теги, вызывать его при запуске

```
osm2pgsql --create --latlong --style shops.style --database gis $dump-filtered.osm.pbf
```

Ну а дальше берёшь PostGIS и выполняешь в нём SQL-запросы, реляционные СУБД именно для такого и придумали в 80-х.

## Объединение полигональных и точечных POI

```
DROP TABLE IF EXISTS shops;
CREATE TABLE shops AS 
(
SELECT 
id,
shop,
amenity,
name,
ST_PointOnSurface(geom) AS wkb_geometry
FROM planet_osm_polygon

UNION

SELECT 
id,
shop,
amenity,
name,
ST_PointOnSurface(geom) AS wkb_geometry
FROM planet_osm_point
)
```

## Запросы

```
SELECT * 
FROM shops
WHERE name = 'Продукты';

```



```
SELECT * 
FROM shops
WHERE name LIKE 'Продукт%';
```
Оператор LIKE: Знак процента ( %)  для сравнения любого числа символов. Нижнее подчёркивание ( _)  для сравнения любого одного символа.
Оператор ILIKE - регистронезависимый
```
SELECT * 
FROM shops
WHERE name IN ('Продукты','Промтовары');

SELECT * 
FROM shops
WHERE name IN ('Продукты','Промтовары') OR operator ILIKE 'Мария-Ра' ;
```

## Получение количества записей

```
SELECT COUNT(*) AS cnt 
FROM shops
WHERE name IN ('Продукты','Промтовары');
```
