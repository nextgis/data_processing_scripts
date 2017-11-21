DROP TABLE IF EXISTS intersections;
DROP TABLE IF EXISTS joining_union;
DROP TABLE IF EXISTS joining_segments;

CREATE TABLE intersections AS 
SELECT DISTINCT (ST_DUMP(ST_INTERSECTION(a.wkb_geometry, b.wkb_geometry))).geom AS ix 
FROM joining a 
INNER JOIN joining b 
ON ST_INTERSECTS(a.wkb_geometry,b.wkb_geometry)
WHERE geometrytype(st_intersection(a.wkb_geometry,b.wkb_geometry)) = 'POINT';

/*
CREATE INDEX ON intersections USING gist(ix);

CREATE TABLE joining_union AS 
SELECT ST_UNION(wkb_geometry) as wkb_geometry
FROM joining;

CREATE INDEX ON joining_union USING gist(wkb_geometry);

CREATE TABLE joining_segments AS
SELECT (ST_DUMP(ST_SPLIT(a.wkb_geometry,b.ix))).geom AS wkb_geometry
FROM joining_union a
INNER JOIN intersections b
ON ST_INTERSECTS(a.wkb_geometry, b.ix);

ALTER TABLE joining_segments ADD COLUMN id SERIAL PRIMARY KEY;

DROP TABLE intersections;
DROP TABLE joining_union;
*/



DROP TABLE IF EXISTS split;
CREATE TABLE split AS(
SELECT
    (ST_Dump(ST_Split(ST_Snap(a.wkb_geometry, b.ix, 0.00001),b.ix))).geom AS wkb_geometry,
    a.highway
FROM 
    joining a
JOIN 
    intersections b 
ON 
    ST_DWithin(b.ix, a.wkb_geometry, 0.00001)
);

ALTER TABLE split ADD COLUMN id SERIAL PRIMARY KEY;
CREATE INDEX ON split USING gist(wkb_geometry);
