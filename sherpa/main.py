from pathlib import Path
from typing import Optional

from typer import Typer, Option, Argument

from sherpa.constants import CONFIG_FILE
from sherpa.utils import load_config, print_config, write_config
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


@app.command(name="list")
def list_tables(schema: str = Option("public", "--schema", "-s", help="Schema of tables to list")) -> None:
    """
    List tables in a specified schema (default: public)
    """
    current_config = load_config()
    client = PgClient(current_config["default"]["dsn"])
    client.list_tables(schema)


@app.command()
def load(
    file: Path = Argument(..., help="Path to file to load"),
    table: str = Argument(..., help="Name of table to load to"),
    schema: str = Option("public", "--schema", "-s", help="Schema of table to load to"),
    batch_size: int = Option(1000, "--batch-size", "-b", help="Number of records to insert at once"),
) -> None:
    """
    Load a file to a PostGIS table
    """
    current_config = load_config()
    client = PgClient(current_config["default"]["dsn"])
    client.load(file, table, schema, batch_size)


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database.
    """
