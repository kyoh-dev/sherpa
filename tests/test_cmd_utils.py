import pytest

from sherpa.cmd_utils import load_config, print_config, write_config


def test_load_config_no_file(capsys, config_dir):
    with pytest.raises(SystemExit) as ex:
        load_config(config_dir / "config")
    assert ex.type == SystemExit
    assert ex.value.code == 1
    assert "Error: Config does not exist" in capsys.readouterr().out


def test_load_config_with_file(config_file, default_config):
    config = load_config(config_file)
    assert config == default_config


def test_print_config(capsys, config_file, default_config):
    print_config(config_file)
    output = capsys.readouterr().out
    for k, v in default_config["default"].items():
        assert f"{k}={v}" in output


def test_write_config(config_file, default_config):
    write_config(config_file, default_config['default'])
    config = load_config(config_file)
    assert config == default_config
