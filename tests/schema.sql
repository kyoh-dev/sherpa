CREATE TABLE public.geojson_test (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    polygon_id INT NOT NULL,
    geometry GEOMETRY(Polygon, 4326) NOT NULL
);

CREATE TABLE public.gpkg_test (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    polygon_id INT NOT NULL,
    geometry GEOMETRY(Polygon, 4283) NOT NULL
);
