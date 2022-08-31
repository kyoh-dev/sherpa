import pytest
import toml


@pytest.fixture
def default_config():
    yield {
        "default": {
            "user": "test",
            "password": "test",
            "dbname": "sherpa-test",
            "host": "sherpadb",
            "port": "5432",
            "dsn": "postgres://test:test@sherpadb:5432/sherpa-test",
        }
    }


@pytest.fixture
def config_dir(tmp_path):
    yield tmp_path / ".sherpa"


@pytest.fixture
def config_file(tmp_path, default_config, config_dir):
    test_config_file = config_dir / "config"
    config_dir.mkdir()
    with open(test_config_file, "w") as f:
        toml.dump(default_config, f)
    yield test_config_file
