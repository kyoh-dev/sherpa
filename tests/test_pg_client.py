import pytest
import fiona
from psycopg2.sql import SQL, Identifier, Composed

from sherpa.pg_client import PgTable, generate_row_data, generate_sql_insert_row, generate_sql_transforms

from tests.constants import TEST_TABLE


@pytest.fixture
def pg_table(dsn_profile):
    yield PgTable("public", TEST_TABLE, ["polygon_id", "geometry"])


def test_get_insert_table_info(pg_client):
    table = pg_client.get_insert_table_info(TEST_TABLE)
    assert table.table == TEST_TABLE
    assert table.columns == ["polygon_id", "geometry"]
    assert table.sql_composed_columns == Composed([Identifier("polygon_id"), SQL(", "), Identifier("geometry")])


@pytest.mark.parametrize(
    "schema, expected_result",
    [
        pytest.param("public", True, id="public"),
        pytest.param("generic", True, id="generic"),
        pytest.param("non_existent", False, id="non_existent"),
    ],
)
def test_schema_exists(pg_client, schema, expected_result):
    assert expected_result == pg_client.schema_exists(schema)


@pytest.mark.parametrize("file", [pytest.param("geojson_file", id="geojson"), pytest.param("gpkg_file", id="gpkg")])
def test_load_success(request, pg_client, pg_connection, pg_table, file):
    pg_client.load(request.getfixturevalue(file), pg_table)
    with pg_connection.cursor() as cursor:
        cursor.execute(
            SQL(
                """
            SELECT
              polygon_id,
              geometry
            FROM public.{}
            """
            ).format(Identifier(TEST_TABLE))
        )
        results = cursor.fetchall()

    assert results == [
        (
            "ABC123",
            "0103000020E61000000100000004000000235F53311F9462407C992842EAA841C0EE9E97E546946240A898391389A941C07FE5F7ECEF93624046B1DCD26AA941C0235F53311F9462407C992842EAA841C0",
        ),
        (
            "ABC123",
            "0103000020E610000001000000040000005673CAED68946240E902A8F3F2A941C0D913138AA39462400C90680245A941C0C5B01E52A7946240D4974AE427AA41C05673CAED68946240E902A8F3F2A941C0",
        ),
        (
            "DEF456",
            "0103000020E61000000100000004000000D1FEAC9EF8946240E2B9ADE3AEA941C09BBA3CE7389562408FF4B3A217A941C09BBA3CE73895624072B0EDA309AA41C0D1FEAC9EF8946240E2B9ADE3AEA941C0",
        ),
        (
            "GHI789",
            "0103000020E6100000010000000400000090F06206CF9462405B83520F2CA741C095511B8B1C956240D81E076F59A741C0A3CFA2D2E3946240A026E9503CA841C090F06206CF9462405B83520F2CA741C0",
        ),
    ]


def test_create_table_from_file_success(pg_client, pg_connection, geojson_file):
    pg_client.create_table(geojson_file, "generic", "test_geojson_file")
    with pg_connection.cursor() as cursor:
        cursor.execute(
            SQL(
                """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'generic'
                AND tablename = 'test_geojson_file'
            """
            ).format(Identifier(geojson_file.name.removesuffix(geojson_file.suffix)))
        )
        results = cursor.fetchone()[0]

    assert results == "test_geojson_file"


def test_generate_row_data(geojson_file, pg_table):
    with fiona.open(geojson_file) as collection:
        rows = list(generate_row_data(collection, pg_table))

    assert rows == [
        (
            "ABC123",
            '{"type": "Polygon", "coordinates": [[[148.6288077, -35.319649], [148.6336544, -35.3244957], [148.6230378, -35.3235725], [148.6288077, -35.319649]]]}',
        ),
        (
            "ABC123",
            '{"type": "Polygon", "coordinates": [[[148.6378087, -35.3277268], [148.6449633, -35.3224185], [148.6454249, -35.3293424], [148.6378087, -35.3277268]]]}',
        ),
        (
            "DEF456",
            '{"type": "Polygon", "coordinates": [[[148.6553491, -35.3256497], [148.6631962, -35.3210338], [148.6631962, -35.3284192], [148.6553491, -35.3256497]]]}',
        ),
        (
            "GHI789",
            '{"type": "Polygon", "coordinates": [[[148.6502716, -35.3060321], [148.6597343, -35.3074168], [148.6528104, -35.3143407], [148.6502716, -35.3060321]]]}',
        ),
    ]


def test_generate_sql_transforms(pg_table):
    transforms = generate_sql_transforms(pg_table)
    assert transforms == ["%s", "ST_GeomFromGeoJSON(%s)"]


def test_generate_sql_insert_row(pg_table, pg_connection):
    row_data = (
        "ABC123",
        '{"type": "Polygon", "coordinates": [[[148.6288077, -35.319649], [148.6336544, -35.3244957], [148.6230378, -35.3235725], [148.6288077, -35.319649]]]}',
    )
    with pg_connection.cursor() as cursor:
        sql_insert_rows = generate_sql_insert_row(pg_table, row_data, cursor)

    assert sql_insert_rows == Composed(
        [
            SQL("("),
            SQL(
                '\'ABC123\',ST_GeomFromGeoJSON(\'{"type": "Polygon", "coordinates": [[[148.6288077, -35.319649], [148.6336544, -35.3244957], [148.6230378, -35.3235725], [148.6288077, -35.319649]]]}\')'
            ),
            SQL(")"),
        ]
    )
