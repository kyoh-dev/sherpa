from typing import Optional

import toml
from typer import Option, Typer

from sherpa.constants import CONFIG_FILE
from sherpa.utils import print_config, write_config, check_config
from sherpa.pg_client import PgClient

app = Typer(name="sherpa")


@app.command()
def config(list_all: Optional[bool] = Option(False, "--list", "-l", help="List all config options")) -> None:
    """
    Get and set configuration options
    """
    if list_all:
        print_config()
    else:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.parent.mkdir(exist_ok=True)

        write_config()


@check_config
@app.command(name="list")
def list_tables(schema: str = Option("public", "--schema", "-s", help="Schema of tables to list")) -> None:
    """
    List tables in a specified schema (default: public)
    """
    current_config = toml.load(CONFIG_FILE)
    client = PgClient(current_config["default"]["dsn"])
    client.list_tables()


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database.
    """
