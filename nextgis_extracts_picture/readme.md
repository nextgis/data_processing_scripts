# extract picture
take nextgis data extract archive, generate image using qgis render in terminal

# Usage

В каталог extract кладётся распакованый проект. 

В /extract копируется файл проекта, в который добавлен layout с атласом из 1 листа, охват атласа настроен по слою highways. 
Таким образом можно при настройке проекта визуально подогнать соотношение сторон, размер, dpi, а при рендеринге охват будет расчитывать сам qgis и накидывать или отнимать от него проценты.

```
docker build -t nextgis_extract_picture:1.0 .

docker run -it -v ${pwd}:/data   nextgis_extract_picture:1.0  python3 run.py
```

# Features
