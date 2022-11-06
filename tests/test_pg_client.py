import pytest
from psycopg2 import connect
from psycopg2.sql import SQL, Identifier
from rich.table import Table

from sherpa.pg_client import PgClient
from tests.constants import TEST_TABLE


def truncate_tables(config):
    conn = connect(**config)
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(SQL("TRUNCATE TABLE {} CASCADE").format(Identifier(TEST_TABLE)))
    conn.close()


@pytest.fixture
def pg_connection(default_config):
    conn = connect(**default_config["default"])
    yield conn
    conn.close()
    # If a SQL transaction is aborted, all subsequent SQL commands will be ignored
    # so reopening the connection to drop test data is necessary
    truncate_tables(default_config["default"])


@pytest.fixture
def pg_client(default_config):
    yield PgClient(default_config["default"])
    truncate_tables(default_config["default"])


@pytest.fixture
def rich_table():
    table = Table("SCHEMA", "TABLE", "ROWS")
    yield table


@pytest.mark.parametrize(
    "file", [
        pytest.param("geojson_file", id="geojson"),
        pytest.param("gpkg_file", id='gpkg')
    ]
)
def test_load_success(request, pg_client, pg_connection, file):
    pg_client.load(request.getfixturevalue(file), TEST_TABLE)
    with pg_connection.cursor() as cursor:
        cursor.execute(SQL(
            """
            SELECT
              polygon_id,
              geometry
            FROM public.{}
            """
        ).format(Identifier(TEST_TABLE)))
        results = cursor.fetchall()

    assert results == [
        ("ABC123", "0103000020E61000000100000004000000235F53311F9462407C992842EAA841C0EE9E97E546946240A898391389A941C07FE5F7ECEF93624046B1DCD26AA941C0235F53311F9462407C992842EAA841C0"),
        ("ABC123", "0103000020E610000001000000040000005673CAED68946240E902A8F3F2A941C0D913138AA39462400C90680245A941C0C5B01E52A7946240D4974AE427AA41C05673CAED68946240E902A8F3F2A941C0"),
        ("DEF456", "0103000020E61000000100000004000000D1FEAC9EF8946240E2B9ADE3AEA941C09BBA3CE7389562408FF4B3A217A941C09BBA3CE73895624072B0EDA309AA41C0D1FEAC9EF8946240E2B9ADE3AEA941C0"),
        ("GHI789", "0103000020E6100000010000000400000090F06206CF9462405B83520F2CA741C095511B8B1C956240D81E076F59A741C0A3CFA2D2E3946240A026E9503CA841C090F06206CF9462405B83520F2CA741C0")
    ]


def test_list_table_counts_no_data(pg_client, rich_table):
    table = pg_client.list_table_counts()
    rich_table.add_row("public", TEST_TABLE, "0")

    assert table.row_count == rich_table.row_count
    assert table.columns == rich_table.columns
    assert table.rows == rich_table.rows
