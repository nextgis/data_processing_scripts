
--Создать точки на всех их узлах

SELECT (dumppoints).path[1], (dumppoints).geom FROM
(select ST_DumpPoints(wkb_geometry) AS dumppoints from user_highways) AS sub1;

--Пока работа идёт с таблицей linestring

--Найти пересечения новых линий между собой.
--Добавить пересечения новых линий в линии.

DROP TABLE IF EXISTS intersections;
DROP TABLE IF EXISTS joining_union;
DROP TABLE IF EXISTS joining_segments;

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

CREATE TABLE joining_segments AS
SELECT (ST_DUMP(ST_SPLIT(a.geom,b.ix))).geom AS wkb_geometry,
ROW_NUMBER () OVER () as id
FROM joining_union a
INNER JOIN intersections b
ON ST_INTERSECTS(a.geom, b.ix)
GROUP BY wkb_geometry;

-- получился слой joining_segments с линиями, разрезаными по перекрёсткам, но без атрибутов
-- надо заменить на joining_segments


-- =============================================================================

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
