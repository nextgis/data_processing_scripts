На входе - нефильтрованный файл pbf. 

На выходе - geojson с полигонами районов. Фильтрация по тегу admin_level=6.


Для ручного экспорта команда (укажите свой логин и пароль)

``
ogr2ogr -progress -f "GeoJSON" Districts.geojson PG:"host=192.168.250.1 dbname=processing_osm_ch1 user= password=" "planet_osm_polygon"
``
