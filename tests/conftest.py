import pytest
import toml
import fiona


@pytest.fixture
def default_config():
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
def config_file(tmp_path, default_config, config_dir):
    test_config_filepath = config_dir / "config"
    config_dir.mkdir()
    with open(test_config_filepath, "w") as f:
        toml.dump(default_config, f)
    yield test_config_filepath


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
