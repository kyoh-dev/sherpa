import pytest
from typer.testing import CliRunner

from sherpa.cmd import dsn


@pytest.fixture
def runner(monkeypatch, dsn_file, pg_client):
    monkeypatch.setattr(dsn, "DSN_FILEPATH", dsn_file)
    yield CliRunner()


# def test_cmd_list_dsn_profile(runner, dsn_profile):
#     result = runner.invoke(dsn.app, ["ls"])
#     assert result.exit_code == 0
#     for k, v in dsn_profile["default"].items():
#         assert f"{k}={v}" in result.stdout if k != "password" else f"{k}=****"
