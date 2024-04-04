from pathlib import Path

import pytest
from typer.testing import CliRunner

from sherpa import main
from tests.constants import TEST_TABLE


@pytest.fixture
def runner(monkeypatch, config_file, pg_client):
    monkeypatch.setattr(main, "CONFIG_FILE", config_file)
    yield CliRunner()


def test_cmd_config_list_all(runner, default_config):
    result = runner.invoke(main.app, ["config", "--list"])
    assert result.exit_code == 0
    for k, v in default_config["default"].items():
        assert f"{k}={v}" in result.stdout if k != "password" else f"{k}=****"


def test_cmd_config_valid_dsn(runner):
    result = runner.invoke(main.app, ["config"], input="postgres://test:test@sherpadb:5432/sherpa-test\n")
    assert result.exit_code == 0
    assert "Config saved!" in result.stdout


def test_cmd_config_invalid_dsn(runner):
    result = runner.invoke(main.app, ["config"], input="wrongdb://test:test@sherpadb:5432/sherpa-test\n")
    assert result.exit_code == 1
    assert "Error: Invalid connection string" in result.stdout


def test_cmd_list_tables_default_schema(runner):
    result = runner.invoke(main.app, ["tables"])
    expected_output = {"SCHEMA": "public", "TABLE": TEST_TABLE, "ROWS": "0"}
    assert result.exit_code == 0
    for col_header, col_value in expected_output.items():
        assert col_header in result.stdout
        assert col_value in result.stdout


def test_cmd_list_tables_unknown_schema(runner):
    result = runner.invoke(main.app, ["tables", "--schema", "monkeys_in_space"])
    assert result.exit_code == 1
    assert "Error: schema not found" in result.stdout


def test_cmd_load_success(runner, geojson_file):
    result = runner.invoke(main.app, ["load", "--table", TEST_TABLE, str(geojson_file)])
    assert result.exit_code == 0
    assert f"Success: loaded 4 records to public.{TEST_TABLE}" in result.stdout


def test_cmd_load_file_not_found(runner):
    filepath = Path("test_file.geojson")
    result = runner.invoke(main.app, ["load", "--table", TEST_TABLE, str(filepath)])
    assert result.exit_code == 1
    assert "Error: File not found: test_file.geojson" in result.stdout


def test_cmd_load_unknown_table(runner, geojson_file):
    result = runner.invoke(main.app, ["load", "--table", "monkeys_in_space", str(geojson_file)])
    assert result.exit_code == 1
    assert "Error: unable to get table structure for public.monkeys_in_space" in result.stdout


def test_cmd_load_create_table(runner, geojson_file, pg_connection):
    result = runner.invoke(main.app, ["load", "--create", str(geojson_file)])
    assert result.exit_code == 0

    with pg_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                polygon_id,
                geometry
            FROM public.test_geojson_file
            """
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


def test_cmd_load_no_table_input(runner, geojson_file):
    result = runner.invoke(main.app, ["load", str(geojson_file)])
    assert result.exit_code == 1
    assert "Error: you must provide a table name or the --create option" in result.stdout
