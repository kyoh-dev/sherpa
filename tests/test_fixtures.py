import pytest
import fiona


@pytest.mark.parametrize(
    "file, crs", [
        pytest.param("geojson_file", {"init": "epsg:4326"}, id="geojson_file"),
        pytest.param("gpkg_file", {"init": "epsg:4283"}, id="gpkg_file")
    ]
)
def test_geometry_file_fixtures(request, file, crs, geometry_records):
    with fiona.open(request.getfixturevalue(file)) as collection:
        assert collection.crs == crs
        assert len(list(collection.values())) == len(geometry_records)
