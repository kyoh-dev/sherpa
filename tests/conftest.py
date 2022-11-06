import pytest
import toml


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
