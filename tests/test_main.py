from pathlib import Path

import pytest
from typer.testing import CliRunner

from sherpa import main
from tests.constants import TEST_TABLE


@pytest.fixture
def runner(monkeypatch, dsn_profile, pg_client):
    monkeypatch.setattr("sherpa.main.read_dsn_file", lambda: dsn_profile)
    yield CliRunner()


def test_cmd_load_success(runner, geojson_file):
    result = runner.invoke(main.app, ["load", str(geojson_file), TEST_TABLE, "--srid", 4326])
    assert result.exit_code == 0
    assert f"sherpa: Loaded 4 records to public.{TEST_TABLE}" in result.stdout


def test_cmd_load_file_not_found(runner):
    filepath = Path("test_file.geojson")
    result = runner.invoke(main.app, ["load", str(filepath), TEST_TABLE])
    assert result.exit_code == 1
    assert "sherpa: File not found: test_file.geojson" in result.stdout


def test_cmd_load_table_not_found(runner, geojson_file):
    result = runner.invoke(main.app, ["load", str(geojson_file), "monkeys_in_space"])
    assert result.exit_code == 1
    assert "sherpa: Table not found: public.monkeys_in_space" in result.stdout


def test_cmd_load_create_table(runner, geojson_file, pg_connection):
    result = runner.invoke(main.app, ["load", "--create", str(geojson_file), "test_geojson_file"])
    assert result.exit_code == 0

    with pg_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                polygon_id,
                ST_AsText(geometry)
            FROM public.test_geojson_file
            """
        )
        results = cursor.fetchall()

    assert results == [
        (
            "ABC123",
            "POLYGON((148.6288077 -35.319649,148.6336544 -35.3244957,148.6230378 -35.3235725,148.6288077 -35.319649))",
        ),
        (
            "ABC123",
            "POLYGON((148.6378087 -35.3277268,148.6449633 -35.3224185,148.6454249 -35.3293424,148.6378087 -35.3277268))",
        ),
        (
            "DEF456",
            "POLYGON((148.6553491 -35.3256497,148.6631962 -35.3210338,148.6631962 -35.3284192,148.6553491 -35.3256497))",
        ),
        (
            "GHI789",
            "POLYGON((148.6502716 -35.3060321,148.6597343 -35.3074168,148.6528104 -35.3143407,148.6502716 -35.3060321))",
        ),
    ]


def test_cmd_load_no_table_input(runner, geojson_file):
    result = runner.invoke(main.app, ["load", str(geojson_file)])
    print(result.stdout)
    assert result.exit_code == 1
    assert "sherpa: You must provide a table to load to or create one with --create/-c" in result.stdout
