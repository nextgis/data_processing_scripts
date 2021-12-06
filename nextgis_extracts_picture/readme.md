# extract picture
take nextgis data extract archive, generate image using qgis render in terminal

# Usage

```
docker build -t nextgis_extract_picture:1.0 .

docker run -it -v c:\trolleway\1126_qgisrender\zips\:/data   nextgis_extract_picture:1.0 python3 render.py RU-AST.zip RU-AST
docker run -it -v c:\trolleway\1126_qgisrender\zips\:/data   nextgis_extract_picture:1.0 python3 render.py RU-TYU.zip RU-TYU
docker run -it -v c:\trolleway\1126_qgisrender\zips\:/data   nextgis_extract_picture:1.0 python3 render.py RU-SPE.zip RU-SPE
docker run -it -v c:\trolleway\1126_qgisrender\zips\:/data   nextgis_extract_picture:1.0 python3 render.py RU-MOW.zip RU-MOW
```

# Features


В контейнер в каталог extract монтируется каталог где лежат zip с выгрузками.

Код состоит из 2 скриптов:

   pyqgis_client_atlas.py - принимает на вход файл проекта, название layout и имя выходного растра. Скрипт запускает pyqgis, рендрит макет с атласом. Охват атласа настроен по слою extent_region.geojson, который нужно сгенерировать перед запуском скрипта
   render.py - распаковывает архив с выгрузкой в каталог где лежат архивы, генерирует слой охвата, кладёт свой файл проекта, рендрит в 2 картинки

Таким образом можно при настройке проекта визуально подогнать соотношение сторон, размер, dpi, а при рендеринге охват будет расчитывать сам qgis и накидывать или отнимать от него проценты.
