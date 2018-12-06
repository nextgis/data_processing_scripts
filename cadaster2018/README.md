Имеется несколько файлов gpkg, полученых после выгрузки кадастровых кварталов. В них кадастровые кварталы и полигоны запроса.

Склейка файлов (указать имена файлов в скрипте)

```

./ ogrmerge.sh

```

Загрузить в postgis (встасить сюда). Тут в списке полей опущены поля которые конфликтуют с postgis
```
ogr2ogr -overwrite -nlt MULTIPOLYGON -unsetFid  -nln cadastral_units \
-select " cns,  cnid, cnn, adate, anno_text, cs, date_change, lastmodified, local_id, pubdate, reg, oks_count_geo, oks_count_total, oks_adate, parcel_count_geo, parcel_count_total, parcel_adate, is_real_geom" \
-f "PostgreSQL" PG:"dbname=gis user=trolleway" "pkk_merge_filtered.gpkg" "cadastral_units"


```
Выполнить в postgis вручную запрос, который удалит дубликаты по полю

```
DELETE
FROM
    cadastral_units a
        USING cadastral_units b
WHERE
    a.ogc_fid < b.ogc_fid
    AND a.cnn = b.cnn;
```
