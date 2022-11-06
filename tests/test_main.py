import pytest
import fiona

from typer.testing import CliRunner

from sherpa import main


@pytest.fixture
def runner(monkeypatch, config_file):
    monkeypatch.setattr(main, "CONFIG_FILE", config_file)
    yield CliRunner()


def test_geojson_file_fixture(geojson_file, geometry_records):
    with fiona.open(geojson_file) as collection:
        assert collection.crs == {'init': 'epsg:4326'}
        assert len(list(collection.values())) == len(geometry_records)


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
