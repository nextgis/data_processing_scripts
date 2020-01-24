
--Создать точки на всех их узлах

SELECT (dumppoints).path[1], (dumppoints).geom FROM
(select ST_DumpPoints(wkb_geometry) AS dumppoints from user_highways) AS sub1;

--Пока работа идёт с таблицей linestring

--Найти пересечения новых линий между собой.
--Добавить пересечения новых линий в линии.
--Найти пересечения новых линий со старыми
--Добавить точки в новые линии.
--Добавить точки в старые линии.
--Нагенерировать новые таблицы точек и веев, с такой же структурой, как основыне
--Создаётся таблица с такой же структурой, как nodes
DROP TABLE IF EXISTS user_nodes;
CREATE TABLE user_nodes
(
  id bigint NOT NULL,
  version integer NOT NULL,
  user_id integer NOT NULL,
  tstamp timestamp without time zone NOT NULL,
  changeset_id bigint NOT NULL,
  tags hstore,
  geom geometry(Point,4326)
  --CONSTRAINT pk_user_nodes PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

--Наполняется таблица пользовательских точек
INSERT INTO user_nodes
SELECT
ROW_NUMBER () OVER () as id,
1 as version,
0 as user_id,
'2020-01-01' as timestamp,
0 as changeset_id,
'highway=>residential'::hstore as tags,
(dumppoints).geom as geom
FROM
(select user_highways.ogc_fid as uid, ST_DumpPoints(wkb_geometry) AS dumppoints from user_highways) AS sub1;


--ROW_NUMBER () OVER (ORDER BY ogc_fid)
--Добавить записи из новых таблиц в старые.
--Выгнать записи в pbf
