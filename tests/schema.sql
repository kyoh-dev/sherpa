CREATE TABLE public.geometry_load_test (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    polygon_id TEXT NOT NULL,
    geometry GEOMETRY(Polygon, 4326) NOT NULL
);

CREATE SCHEMA generic;
