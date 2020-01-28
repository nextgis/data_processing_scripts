

--Конвертация схемы юзерских линий (перенос атрибутов в hstore)
user_highways
ALTER TABLE user_highways DROP COLUMN IF EXISTS tags;
ALTER TABLE user_highways ADD COLUMN tags hstore;
UPDATE user_highways SET tags=hstore('highway', highway::text)||hstore('maxweight', maxweight::text);
--hstore('new_users', p_new_user_count::text)||hstore('post_count', p_post_count::text)
--Создать точки на всех их узлах

SELECT (dumppoints).path[1], (dumppoints).geom FROM
(select ST_DumpPoints(wkb_geometry) AS dumppoints from user_highways) AS sub1;

--Пока работа идёт с таблицей linestring

--Найти пересечения новых линий между собой.


DROP TABLE IF EXISTS intersections;
DROP TABLE IF EXISTS joining_union;
DROP TABLE IF EXISTS userline_segments;

CREATE TABLE intersections AS
SELECT DISTINCT (ST_DUMP(ST_INTERSECTION(a.wkb_geometry, b.wkb_geometry))).geom AS ix
FROM user_highways a
INNER JOIN user_highways b
ON ST_INTERSECTS(a.wkb_geometry,b.wkb_geometry)
WHERE geometrytype(st_intersection(a.wkb_geometry,b.wkb_geometry)) = 'POINT';

CREATE INDEX ON intersections USING gist(ix);

CREATE TABLE joining_union AS
SELECT ST_UNION(wkb_geometry) as geom
FROM user_highways;

CREATE INDEX ON joining_union USING gist(geom);

CREATE TABLE userline_segments AS
SELECT (ST_DUMP(ST_SPLIT(a.geom,b.ix))).geom AS wkb_geometry,
ROW_NUMBER () OVER () as id
FROM joining_union a
INNER JOIN intersections b
ON ST_INTERSECTS(a.geom, b.ix)
GROUP BY wkb_geometry;
--подтягивание атрибутов
ALTER TABLE userline_segments DROP COLUMN IF EXISTS tags;
ALTER TABLE userline_segments ADD COLUMN tags hstore;

UPDATE userline_segments
SET tags = user_highways.tags
FROM
user_highways
WHERE
ST_DWithin(ST_LineInterpolatePoint(userline_segments.wkb_geometry,0.5),user_highways.wkb_geometry,0.0001);
DROP TABLE IF EXISTS intersections;
DROP TABLE IF EXISTS joining_union;
-- получился слой userline_segments с линиями, разрезаными по перекрёсткам, но без атрибутов

-- ДОСЮДА ВРОДЕ ОК

-- для нахождения пересечений дампа и графа нужно собрать таблицу геометрий линий графа

--разворачивание массива со списком нодов в вее в отдельную таблицу, приклеивание к ней геометрии точек
DROP TABLE IF EXISTS nodes_ways;
CREATE TABLE nodes_ways AS
(
SELECT subquery.*, row_number() OVER (PARTITION BY way_id) AS node_order, row_number() OVER () AS id FROM
( SELECT unnest(ways.nodes) AS node_id,
ways.id AS way_id
FROM ways
WHERE ways.tags ? 'highway' ) AS subquery
);

ALTER TABLE nodes_ways ADD PRIMARY KEY(id);
SELECT * FROM nodes_ways;
ALTER TABLE nodes_ways ADD COLUMN wkb_geometry geometry(Point,4326);
UPDATE nodes_ways
SET wkb_geometry = nodes.geom
FROM
nodes
WHERE
nodes.id=nodes_ways.node_id;

-- сборка linestrings
DROP TABLE IF EXISTS ways_linestrings;
CREATE TABLE ways_linestrings AS TABLE ways;
DELETE FROM ways_linestrings WHERE tags ? 'highway' = false;

SELECT * FROM ways_linestrings;
ALTER TABLE ways_linestrings ADD COLUMN wkb_geometry geometry(Linestring,4326);
--ALTER TABLE ways_linestrings ADD COLUMN points array geometry(Linestring,4326);

UPDATE ways_linestrings
SET wkb_geometry = subquery.wkb_geometry
FROM
(SELECT nodes_ways.way_id, ST_MakeLine(nodes_ways.wkb_geometry ORDER BY node_order::bigint) As wkb_geometry	FROM nodes_ways	GROUP BY way_id
) as subquery

WHERE
subquery.way_id=ways_linestrings.id;

SELECT nodes_ways.way_id, ST_AsText(ST_MakeLine(nodes_ways.wkb_geometry ORDER BY node_order)) As wkb_geometry	FROM nodes_ways	GROUP BY way_id;



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
