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

-- опционально
ENDTEXT
)
