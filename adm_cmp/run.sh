#!/bin/bash

set -x #echo on


admfile='Муниципальные_образования_уровень_6_на 01.01.2018.xlsx'

echo "Reading config...."
source config.cfg

ogr2ogr -progress -overwrite -nln adm -f "PostgreSQL"   PG:"host=$host dbname=$dbname" "$admfile" 

