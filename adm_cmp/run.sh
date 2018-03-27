#!/bin/bash

set -x #echo on


admfile='Муниципальные_образования_уровень_6_на 01.01.2018.xlsx'

echo "Reading config...."
source config.cfg

ogr2ogr -progress -overwrite -nln adm1 -f "PostgreSQL"   PG:"host=$host dbname=$dbname" "$admfile" "Количество МО в субъектах"
ogr2ogr -progress -overwrite -nln adm2 -f "PostgreSQL"   PG:"host=$host dbname=$dbname" "$admfile" "Таблица Наимен. и ОКТМО"
ogr2ogr -progress -overwrite -nln adm3 -f "PostgreSQL"   PG:"host=$host dbname=$dbname" "$admfile" "Имена полей"


admfile='adm6.gpkg'

ogr2ogr -progress -overwrite -nln admosm -nlt MULTIPOLYGON -f "PostgreSQL"   PG:"host=$host dbname=$dbname" "$admfile" 


SQL=$(cat <<-ENDTEXT
ALTER TABLE adm2 RENAME COLUMN "field1" TO name_legal;
ALTER TABLE adm2 RENAME COLUMN "field2" TO "type";
ALTER TABLE adm2 RENAME COLUMN "field3" TO "OKATO";
ALTER TABLE adm2 RENAME COLUMN "field4" TO "OKTMO";
ALTER TABLE adm2 RENAME COLUMN "field5" TO "name";
ALTER TABLE adm2 RENAME COLUMN "field6" TO "OKTMO_SUB";
ALTER TABLE adm2 RENAME COLUMN "field7" TO "REGION";

ENDTEXT
)

SQL=$(cat <<-ENDTEXT

/*
Имеется таблица в Excel с районами, и выгрузка районов из OSM.
В OSM районов меньше, чем в Excel.
Запрос выводит записи из таблицы, для которых не нашлось соответствующх объектов в OSM.
В столбцах записаны разные варианты записей, по которым искалось соответствие.

*/

CREATE OR REPLACE FUNCTION normalize_name (character varying)
RETURNS character varying AS $name_normalized$
declare
  name_normalized character varying;
BEGIN
   SELECT trim(regexp_replace(regexp_replace($1 ,'город-курорт|Город|поселок|муниципальный','','i'),' +',' ','g')) INTO name_normalized ;
   RETURN name_normalized;
END;
$name_normalized$ LANGUAGE plpgsql;


ALTER TABLE adm2 DROP COLUMN IF EXISTS name_normalized;
ALTER TABLE adm2 ADD COLUMN name_normalized character varying;
UPDATE  adm2 SET name_normalized = normalize_name(name);
--второй вариант имени, "город Пенза --> городской округ Пенза"
ALTER TABLE adm2 DROP COLUMN IF EXISTS name_normalized_v2;
ALTER TABLE adm2 ADD COLUMN name_normalized_v2 character varying;
UPDATE  adm2 SET name_normalized_v2 = concat(type,' ',normalize_name(name));
--третий вариант имени, "Лысьвенский --> Лысьвенский городской округ"
ALTER TABLE adm2 DROP COLUMN IF EXISTS name_normalized_v3;
ALTER TABLE adm2 ADD COLUMN name_normalized_v3 character varying;
UPDATE  adm2 SET name_normalized_v3 = concat(normalize_name(name),' ',type);

DROP TABLE IF EXISTS compare_f1 ;
CREATE TABLE compare_f1 AS 
SELECT 
admosm.name, 
admosm.admin_lvl,
normalize_name(adm2.name) AS name_normalized,
ST_AsText(ST_Centroid(admosm.wkb_geometry)) as geom 
FROM 
admosm JOIN adm2 ON(
       adm2.name = admosm.name 
    OR adm2.name_normalized = admosm.name 
    OR adm2.name_normalized_v2 = admosm.name 
    OR adm2.name_normalized_v3 = admosm.name 
    )
  ;


--Записи из екселя, которые не нашлись в осм
SELECT 
bigtable.type AS excel_type,
bigtable.name AS excel_name,
bigtable.name_normalized AS excel_name_normalized_v1,
bigtable.name_normalized_v2 AS excel_name_normalized_v2,
bigtable.name_normalized_v3 AS excel_name_normalized_v3
 
FROM   adm2 AS bigtable 
WHERE  NOT EXISTS (
   SELECT 1              -- it's mostly irrelevant what you put here
   FROM   compare_f1 AS smalltable
   WHERE  smalltable.name_normalized = bigtable.name_normalized
   )
ORDER BY name   ;


/*
Верхняя Пышма


*/


ENDTEXT
)
