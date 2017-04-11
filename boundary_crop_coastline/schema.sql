-- DROP TABLE public.grid4326used;

CREATE TABLE public.grid4326used
(
  wkb_geometry geometry,
  x integer,
  y integer,
  key_column bigint NOT NULL DEFAULT nextval('grid4326used_key_column_seq'::regclass),
  CONSTRAINT grid4326used_pkey PRIMARY KEY (key_column)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.grid4326used
  OWNER TO trolleway;

-- Index: public."grid4326used-index"

-- DROP INDEX public."grid4326used-index";

CREATE INDEX "grid4326used-index"
  ON public.grid4326used
  USING gist
  (wkb_geometry);

-- Index: public."grid4326used-key_column"

-- DROP INDEX public."grid4326used-key_column";

CREATE INDEX "grid4326used-key_column"
  ON public.grid4326used
  USING btree
  (key_column);



-- DROP SEQUENCE public.grid_export_key_column_seq;

CREATE SEQUENCE public.grid_export_key_column_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 12038
  CACHE 1;
ALTER TABLE public.grid_export_key_column_seq
  OWNER TO trolleway;


-- DROP TABLE public.grid_export;

CREATE TABLE public.grid_export
(
  wkb_geometry geometry,
  x integer,
  y integer,
  key_column bigint NOT NULL DEFAULT nextval('grid_export_key_column_seq'::regclass),
  CONSTRAINT grid_export_pkey PRIMARY KEY (key_column)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.grid_export
  OWNER TO trolleway;

-- Index: public."grid_export-index"

-- DROP INDEX public."grid_export-index";

CREATE INDEX "grid_export-index"
  ON public.grid_export
  USING gist
  (wkb_geometry);

-- Index: public."grid_export-key_column"

-- DROP INDEX public."grid_export-key_column";

CREATE INDEX "grid_export-key_column"
  ON public.grid_export
  USING btree
  (key_column);











-- Table: public.special_point2

-- DROP TABLE public.special_point2;

CREATE TABLE public.special_point2
(
  wkb_geometry geometry(Point,4326),
  osm_id bigint,
  name text,
  aerialway text,
  aeroway text,
  amenity text,
  area text,
  barrier text,
  building text,
  craft text,
  historic text,
  leisure text,
  military text,
  place text,
  public_transport text,
  railway text,
  shop text,
  sport text,
  "natural" text,
  tourism text,
  key_column bigint NOT NULL DEFAULT nextval('special_point2_key_column_seq'::regclass),
  CONSTRAINT special_point2_pkey PRIMARY KEY (key_column)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.special_point2
  OWNER TO trolleway;

-- Index: public."special_point2-key_column"

-- DROP INDEX public."special_point2-key_column";

CREATE INDEX "special_point2-key_column"
  ON public.special_point2
  USING btree
  (key_column);






