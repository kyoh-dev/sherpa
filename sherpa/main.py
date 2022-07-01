from typing import Optional

import toml
from psycopg2 import ProgrammingError
from psycopg2.extensions import parse_dsn
from typer import Option, Typer, Exit, echo, prompt

from sherpa.constants import CONFIG_FILE
from sherpa.utils import print_config, write_config

app = Typer(name="sherpa")


@app.command()
def config(
    list_all: Optional[bool] = Option(False, "--list-all", "-l", help="List all config options")
) -> None:
    """
    Get and set configuration options
    """
    if list_all:
        print_config()
    else:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.parent.mkdir(exist_ok=True)

        write_config()


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database.
    """
