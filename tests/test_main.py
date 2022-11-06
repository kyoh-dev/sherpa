import pytest

from typer.testing import CliRunner

from sherpa import main
from tests.constants import TEST_TABLE


@pytest.fixture
def runner(monkeypatch, config_file):
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
    expected_output = {
        "SCHEMA": "public",
        "TABLE": TEST_TABLE,
        "ROWS": "0"
    }
    assert result.exit_code == 0
    for col_header, col_value in expected_output.items():
        assert col_header in result.stdout
        assert col_value in result.stdout


def test_cmd_list_tables_unknown_schema(runner):
    result = runner.invoke(main.app, ["tables", "--schema", "monkeys_in_space"])
    assert result.exit_code == 1
    assert "Error: schema not found" in result.stdout
