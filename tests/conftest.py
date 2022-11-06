import pytest


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
