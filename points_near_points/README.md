На входе - точки (crossings), точки событий (dtp2014).
Для перекрёстков строится 3 буфера, они объединяются.
Делается spatial self join, и подсчитывается количество и разные суммы атрибутов аварий у перекрёстков.
На выходе - полигональный слой с кружками вокруг пеерекрёстков и разными атрибутами.
Скрипт недописан, но комманды работают


```
ogr2ogr -progress -overwrite PG:"host=localhost dbname=gis " ../moscow_crossings.gpkg

ogr2ogr -progress -overwrite -f GPKG dtp2014.gpkg --config SHAPE_ENCODING cp1251  dtp_post_14_all_Mow.shp -skipfailures 
ogr2ogr -progress -overwrite PG:"host=localhost dbname=gis " dtp2014.gpkg -skipfailures  -nln dtp2014

ogr2ogr -progress -overwrite -f GPKG dtp2015.gpkg --config SHAPE_ENCODING cp1251  dtp_post_15_all_Mow.shp -skipfailures 
ogr2ogr -progress -overwrite PG:"host=localhost dbname=gis " dtp2015.gpkg -skipfailures  -nln dtp2015

ogr2ogr -progress -overwrite -f GPKG dtp2016.gpkg --config SHAPE_ENCODING cp1251  dtp_post_16_all_Mow.shp -skipfailures 
ogr2ogr -progress -overwrite PG:"host=localhost dbname=gis " dtp2016.gpkg -skipfailures  -nln dtp2016
```
Выполнить SQL

```
CREATE TEMPORARY TABLE buffers100 ON COMMIT DROP AS 
SELECT st_buffer(ST_Transform(wkb_geometry,32637),100) AS wkb_geometry,100 AS buffer_size FROM moscow_crossings WHERE ways_cnt = 4;
CREATE TEMPORARY TABLE buffers50 ON COMMIT DROP AS 
SELECT st_buffer(ST_Transform(wkb_geometry,32637),50) AS wkb_geometry,50 AS buffer_size FROM moscow_crossings WHERE ways_cnt = 4;
CREATE TEMPORARY TABLE buffers20 ON COMMIT DROP AS 
SELECT st_buffer(ST_Transform(wkb_geometry,32637),20) AS wkb_geometry,20 AS buffer_size FROM moscow_crossings WHERE ways_cnt = 4;

/*
CREATE TEMPORARY TABLE crossingsarea ON COMMIT DROP AS 
SELECT * FROM buffers100
UNION
SELECT * FROM buffers50
UNION
SELECT * FROM buffers20;
*/

DROP TABLE IF EXISTS crossingsarea_disolved;
CREATE TABLE crossingsarea_disolved ( 
    wkb_geometry geometry,
    buffer integer);

DROP TABLE IF EXISTS crossingsarea_disolved_onebuffer ;
CREATE 
TEMPORARY 
TABLE crossingsarea_disolved_onebuffer 
ON COMMIT DROP 
AS 
WITH
 clusters(wkb_geometry) AS 
      (SELECT ST_CollectionExtract(unnest(ST_ClusterIntersecting(wkb_geometry)), 3) 
         FROM buffers100),
 multis(id, wkb_geometry) AS 
      (SELECT row_number() over() as id, wkb_geometry FROM clusters)
 SELECT ST_UNION(wkb_geometry) AS wkb_geometry FROM 
      (SELECT id, (ST_DUMP(wkb_geometry)).geom AS wkb_geometry FROM multis) d GROUP BY id;
INSERT INTO  crossingsarea_disolved SELECT wkb_geometry, 100 as buffer FROM crossingsarea_disolved_onebuffer;  


DROP TABLE IF EXISTS crossingsarea_disolved_onebuffer ;
CREATE 
TEMPORARY 
TABLE crossingsarea_disolved_onebuffer 
ON COMMIT DROP 
AS 
WITH
 clusters(wkb_geometry) AS 
      (SELECT ST_CollectionExtract(unnest(ST_ClusterIntersecting(wkb_geometry)), 3) 
         FROM buffers50),
 multis(id, wkb_geometry) AS 
      (SELECT row_number() over() as id, wkb_geometry FROM clusters)
 SELECT ST_UNION(wkb_geometry) AS wkb_geometry FROM 
      (SELECT id, (ST_DUMP(wkb_geometry)).geom AS wkb_geometry FROM multis) d GROUP BY id;
INSERT INTO  crossingsarea_disolved SELECT wkb_geometry, 50 as buffer FROM crossingsarea_disolved_onebuffer;   


DROP TABLE IF EXISTS crossingsarea_disolved_onebuffer ;
CREATE 
TEMPORARY 
TABLE crossingsarea_disolved_onebuffer 
ON COMMIT DROP 
AS 
WITH
 clusters(wkb_geometry) AS 
      (SELECT ST_CollectionExtract(unnest(ST_ClusterIntersecting(wkb_geometry)), 3) 
         FROM buffers20),
 multis(id, wkb_geometry) AS 
      (SELECT row_number() over() as id, wkb_geometry FROM clusters)
 SELECT ST_UNION(wkb_geometry) AS wkb_geometry FROM 
      (SELECT id, (ST_DUMP(wkb_geometry)).geom AS wkb_geometry FROM multis) d GROUP BY id;
INSERT INTO  crossingsarea_disolved SELECT wkb_geometry, 20 as buffer FROM crossingsarea_disolved_onebuffer;   



ALTER TABLE crossingsarea_disolved ADD COLUMN count_2014 integer;
ALTER TABLE crossingsarea_disolved ADD COLUMN count_2015 integer;
ALTER TABLE crossingsarea_disolved ADD COLUMN count_2016 integer;

ALTER TABLE crossingsarea_disolved ADD COLUMN cp_2014 integer;
ALTER TABLE crossingsarea_disolved ADD COLUMN cp_2015 integer;
ALTER TABLE crossingsarea_disolved ADD COLUMN cp_2016 integer;

ALTER TABLE crossingsarea_disolved ADD COLUMN cps_2014 integer;
ALTER TABLE crossingsarea_disolved ADD COLUMN cps_2015 integer;
ALTER TABLE crossingsarea_disolved ADD COLUMN cps_2016 integer;

ALTER TABLE crossingsarea_disolved ADD COLUMN cp_sum integer;
COMMENT ON COLUMN crossingsarea_disolved.cp_sum IS 'КОЛИЧЕСТВО АВАРИЙ С ТРУПАМИ';
ALTER TABLE crossingsarea_disolved ADD COLUMN cps_sum integer;
COMMENT ON COLUMN crossingsarea_disolved.cp_sum IS 'КОЛИЧЕСТВО ТРУПОВ';

UPDATE crossingsarea_disolved SET wkb_geometry=ST_SetSRID(wkb_geometry,32637);
UPDATE crossingsarea_disolved SET count_2014=0;
UPDATE crossingsarea_disolved SET count_2015=0;
UPDATE crossingsarea_disolved SET count_2016=0;
UPDATE crossingsarea_disolved SET cp_2014=0;
UPDATE crossingsarea_disolved SET cp_2015=0;
UPDATE crossingsarea_disolved SET cp_2016=0;
UPDATE crossingsarea_disolved SET cps_2014=0;
UPDATE crossingsarea_disolved SET cps_2015=0;
UPDATE crossingsarea_disolved SET cps_2016=0;

CREATE TEMPORARY TABLE medium2014 ON COMMIT DROP AS 
SELECT
dtp2014.wkb_geometry, crossingsarea_disolved.wkb_geometry AS crossing_geometry,corpse
FROM 
dtp2014 , crossingsarea_disolved
WHERE 
ST_Within(dtp2014.wkb_geometry, crossingsarea_disolved.wkb_geometry);



CREATE TEMPORARY TABLE medium2014_cnt ON COMMIT DROP AS 
SELECT medium2014.crossing_geometry, COUNT(*) AS cnt  FROM medium2014 GROUP BY crossing_geometry;

UPDATE crossingsarea_disolved SET count_2014 = medium2014_cnt.cnt
FROM medium2014_cnt
WHERE medium2014_cnt.crossing_geometry = crossingsarea_disolved.wkb_geometry;
DROP TABLE medium2014_cnt;

CREATE TEMPORARY TABLE medium2014_cnt ON COMMIT DROP AS 
SELECT medium2014.crossing_geometry, COUNT(*) AS cnt, SUM(corpse) AS corpses FROM medium2014 WHERE corpse > 0 GROUP BY crossing_geometry;

UPDATE crossingsarea_disolved SET cp_2014 = medium2014_cnt.cnt, cps_2014 = medium2014_cnt.corpses
FROM medium2014_cnt
WHERE medium2014_cnt.crossing_geometry = crossingsarea_disolved.wkb_geometry;
DROP TABLE medium2014_cnt;


CREATE TEMPORARY TABLE medium2015 ON COMMIT DROP AS 
SELECT
dtp2015.wkb_geometry, crossingsarea_disolved.wkb_geometry AS crossing_geometry,corpse
FROM 
dtp2015 , crossingsarea_disolved
WHERE 
ST_Within(dtp2015.wkb_geometry, crossingsarea_disolved.wkb_geometry);

CREATE TEMPORARY TABLE medium2015_cnt ON COMMIT DROP AS 
SELECT medium2015.crossing_geometry, COUNT(*) AS cnt FROM medium2015 GROUP BY crossing_geometry;

UPDATE crossingsarea_disolved SET count_2015 = medium2015_cnt.cnt
FROM medium2015_cnt
WHERE medium2015_cnt.crossing_geometry = crossingsarea_disolved.wkb_geometry;
DROP TABLE medium2015_cnt;

CREATE TEMPORARY TABLE medium2015_cnt ON COMMIT DROP AS 
SELECT medium2015.crossing_geometry, COUNT(*) AS cnt, SUM(corpse) AS corpses FROM medium2015 WHERE corpse > 0 GROUP BY crossing_geometry;

UPDATE crossingsarea_disolved SET cp_2015 = medium2015_cnt.cnt, cps_2015 = medium2015_cnt.corpses
FROM medium2015_cnt
WHERE medium2015_cnt.crossing_geometry = crossingsarea_disolved.wkb_geometry;
DROP TABLE medium2015_cnt;


CREATE TEMPORARY TABLE medium2016 ON COMMIT DROP AS 
SELECT
dtp2016.wkb_geometry, crossingsarea_disolved.wkb_geometry AS crossing_geometry,corpse
FROM 
dtp2016 , crossingsarea_disolved
WHERE 
ST_Within(dtp2016.wkb_geometry, crossingsarea_disolved.wkb_geometry);

CREATE TEMPORARY TABLE medium2016_cnt ON COMMIT DROP AS 
SELECT medium2016.crossing_geometry, COUNT(*) AS cnt FROM medium2016 GROUP BY crossing_geometry;

UPDATE crossingsarea_disolved SET count_2016 = medium2016_cnt.cnt
FROM medium2016_cnt
WHERE medium2016_cnt.crossing_geometry = crossingsarea_disolved.wkb_geometry;
DROP TABLE medium2016_cnt;

CREATE TEMPORARY TABLE medium2016_cnt ON COMMIT DROP AS 
SELECT medium2016.crossing_geometry, COUNT(*) AS cnt, SUM(corpse) AS corpses FROM medium2016 WHERE corpse > 0 GROUP BY crossing_geometry;

UPDATE crossingsarea_disolved SET cp_2016 = medium2016_cnt.cnt, cps_2016 = medium2016_cnt.corpses
FROM medium2016_cnt
WHERE medium2016_cnt.crossing_geometry = crossingsarea_disolved.wkb_geometry;
DROP TABLE medium2016_cnt;


UPDATE crossingsarea_disolved SET cp_sum = cp_2014+cp_2015+cp_2016;
UPDATE crossingsarea_disolved SET cps_sum = cps_2014+cps_2015+cps_2016;
         


```

```
ogr2ogr -progress -overwrite -f GPKG crossings_dtp.gpkg PG:"host=localhost dbname=gis " crossingsarea_disolved  -skipfailures 

```
