from typing import Any

import pytest
import tomlkit
import fiona
from psycopg2 import connect
from psycopg2.sql import SQL, Identifier

from sherpa.pg_client import PgClient
from tests.constants import TEST_TABLE


def create_test_tables(config: dict[str, Any]) -> None:
    conn = connect(**config)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(
                SQL(
                    """
                CREATE TABLE public.{} (
                    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    polygon_id TEXT NOT NULL,
                    geometry GEOMETRY(Polygon, 4326) NOT NULL
                );

                CREATE SCHEMA generic;
                """
                ).format(Identifier(TEST_TABLE))
            )
    conn.close()


def drop_test_tables(config: dict[str, Any]) -> None:
    conn = connect(**config)
    with conn:
        with conn.cursor() as cursor:
            for table in ("test_geojson_file", "test_gpkg_file", TEST_TABLE):
                cursor.execute(SQL("DROP TABLE IF EXISTS {} CASCADE;").format(Identifier(table)))
            cursor.execute("DROP SCHEMA IF EXISTS generic CASCADE;")
    conn.close()


@pytest.fixture
def pg_client(dsn_profile):
    create_test_tables(dsn_profile["default"])
    client = PgClient(dsn_profile["default"])
    yield client
    client.close()
    drop_test_tables(dsn_profile["default"])


@pytest.fixture
def pg_connection(dsn_profile):
    conn = connect(**dsn_profile["default"])
    yield conn
    conn.close()


@pytest.fixture
def dsn_profile():
    yield {
        "default": {
            "user": "test",
            "password": "test",
            "dbname": "sherpa-test",
            "host": "localhost",
            "port": "27901",
        }
    }


@pytest.fixture
def config_dir(tmp_path):
    yield tmp_path / ".sherpa"


@pytest.fixture
def dsn_file(tmp_path, dsn_profile, config_dir):
    test_dsn_filepath = config_dir / "dsn.toml"
    config_dir.mkdir()
    with open(test_dsn_filepath, "w") as f:
        tomlkit.dump(dsn_profile, f)
    yield test_dsn_filepath


@pytest.fixture
def geometry_records():
    return [
        {
            "type": "Feature",
            "properties": {"polygon_id": "ABC123"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [148.6288077, -35.319649],
                        [148.6336544, -35.3244957],
                        [148.6230378, -35.3235725],
                        [148.6288077, -35.319649],
                    ]
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"polygon_id": "ABC123"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [148.6378087, -35.3277268],
                        [148.6449633, -35.3224185],
                        [148.6454249, -35.3293424],
                        [148.6378087, -35.3277268],
                    ]
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"polygon_id": "DEF456"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [148.6553491, -35.3256497],
                        [148.6631962, -35.3210338],
                        [148.6631962, -35.3284192],
                        [148.6553491, -35.3256497],
                    ]
                ],
            },
        },
        {
            "type": "Feature",
            "properties": {"polygon_id": "GHI789"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [148.6502716, -35.3060321],
                        [148.6597343, -35.3074168],
                        [148.6528104, -35.3143407],
                        [148.6502716, -35.3060321],
                    ]
                ],
            },
        },
    ]


@pytest.fixture
def geojson_file(tmp_path, geometry_records):
    f = tmp_path / "test_geojson_file.geojson"
    schema = {"geometry": "Polygon", "properties": {"polygon_id": "str"}}
    with fiona.open(f, "w", schema=schema, driver="GeoJSON", crs="EPSG:4326") as collection:
        collection.writerecords(geometry_records)
    yield f


@pytest.fixture
def gpkg_file(tmp_path, geometry_records):
    f = tmp_path / "test_gpkg_file.gpkg"
    schema = {"geometry": "Polygon", "properties": {"polygon_id": "str"}}
    with fiona.open(f, "w", schema=schema, driver="GPKG", crs="EPSG:4326") as collection:
        collection.writerecords(geometry_records)
    yield f
