import pytest
from typer.testing import CliRunner
from rich.table import Table

from sherpa.cmd import table

from tests.constants import TEST_TABLE


@pytest.fixture
def runner(monkeypatch, dsn_profile):
    monkeypatch.setattr("sherpa.utils.read_dsn_file", dsn_profile)
    yield CliRunner()


@pytest.fixture
def rich_table():
    table = Table("SCHEMA", "TABLE", "ROWS")
    yield table


def test_cmd_list_tables_no_data(pg_client, runner, rich_table):
    result = runner.invoke(table.app, ["ls"])
    rich_table.add_row("public", TEST_TABLE, "0")
    print(result.stdout)
    assert result.exit_code == 0
    for table_output in ["SCHEMA", "TABLE", "ROWS", "public", "geometry_load_test", "0"]:
        assert table_output in result.stdout


# def test_cmd_list_tables_default_schema(runner):
#     result = runner.invoke(main.app, ["tables"])
#     expected_output = {"SCHEMA": "public", "TABLE": TEST_TABLE, "ROWS": "0"}
#     assert result.exit_code == 0
#     for col_header, col_value in expected_output.items():
#         assert col_header in result.stdout
#         assert col_value in result.stdout
#
#
# def test_cmd_list_tables_unknown_schema(runner):
#     result = runner.invoke(main.app, ["tables", "--schema", "monkeys_in_space"])
#     assert result.exit_code == 1
#     assert "Error: schema not found" in result.stdout
