import pytest
import fiona

from typer.testing import CliRunner

from sherpa import main


@pytest.fixture
def runner(monkeypatch, config_file):
    monkeypatch.setattr(main, "CONFIG_FILE", config_file)
    yield CliRunner()


@pytest.fixture
def geometry_records():
    return [
        {"type": "Feature", "properties": {"polygon_id": "ABC123"}, "geometry": {"type": "Polygon", "coordinates": [[[148.6288077, -35.319649], [148.6336544, -35.3244957], [148.6230378, -35.3235725], [148.6288077, -35.319649]]]}},
        {"type": "Feature", "properties": {"polygon_id": "ABC123"}, "geometry": {"type": "Polygon", "coordinates": [[[148.6378087, -35.3277268], [148.6449633, -35.3224185], [148.6454249, -35.3293424], [148.6378087, -35.3277268]]]}},
        {"type": "Feature", "properties": {"polygon_id": "DEF456"}, "geometry": {"type": "Polygon", "coordinates": [[[148.6553491, -35.3256497], [148.6631962, -35.3210338], [148.6631962, -35.3284192], [148.6553491, -35.3256497]]]}},
        {"type": "Feature", "properties": {"polygon_id": "GHI789"}, "geometry": {"type": "Polygon", "coordinates": [[[148.6502716, -35.3060321], [148.6597343, -35.3074168], [148.6528104, -35.3143407], [148.6502716, -35.3060321]]]}}
    ]


@pytest.fixture
def geojson_file(tmp_path, geometry_records):
    f = tmp_path / "test_geojson_file.geojson"
    schema = {
        "geometry": "Polygon",
        "properties": {"polygon_id": "str"}
    }
    with fiona.open(f, "w", schema=schema, driver="GeoJSON", crs="EPSG:4326") as collection:
        collection.writerecords(geometry_records)
    yield f


def test_geojson_file_fixture(geojson_file, geometry_records):
    with fiona.open(geojson_file) as collection:
        assert collection.crs == {'init': 'epsg:4326'}
        assert len(list(collection.values())) == len(geometry_records)


def test_cmd_config_list_all(runner, default_config):
    result = runner.invoke(main.app, ["config", "--list"])
    assert result.exit_code == 0
    for k, v in default_config["default"].items():
        assert f"{k}={v}" in result.stdout


def test_cmd_config_valid_dsn(runner):
    result = runner.invoke(main.app, ["config"], input="postgres://test:test@sherpadb:5432/sherpa-test\n")
    assert result.exit_code == 0
    assert "Config saved!" in result.stdout


def test_cmd_config_invalid_dsn(runner):
    result = runner.invoke(main.app, ["config"], input="wrongdb://test:test@sherpadb:5432/sherpa-test\n")
    assert result.exit_code == 1
    assert "Error: Invalid connection string" in result.stdout
