from pathlib import Path
from typing import Optional

from typer import Typer, Option, Argument
from psycopg2 import ProgrammingError
from psycopg2.extensions import parse_dsn

from sherpa.constants import CONFIG_FILE, console
from sherpa.utils import load_config, print_config, write_config
from sherpa.pg_client import PgClient

app = Typer(name="sherpa")


@app.command()
def config(list_all: Optional[bool] = Option(False, "--list", "-l", help="List all config options")) -> None:
    """
    Get and set configuration options
    """
    if list_all:
        print_config(CONFIG_FILE)
    else:
        dsn = console.input("[bold]Postgres DSN[/bold]: ")
        try:
            parsed_dsn = parse_dsn(dsn)
        except ProgrammingError:
            console.print("[bold red]Error:[/bold red] Invalid connection string")
            exit(1)
        else:
            write_config(CONFIG_FILE, parsed_dsn)


@app.command(name="tables")
def list_tables(schema: str = Option("public", "--schema", "-s", help="Schema of tables to target")) -> None:
    """
    List tables in a specified schema (default: public)
    """
    current_config = load_config(CONFIG_FILE)
    client = PgClient(current_config["default"])
    table_info = client.list_table_counts(schema)
    console.print(table_info)


@app.command()
def load(
    file: Path = Argument(..., help="Path to file to load"),
    table: str = Argument(..., help="Name of table to load to"),
    schema: str = Option("public", "--schema", "-s", help="Schema of table to load to"),
) -> None:
    """
    Load a file to a PostGIS table
    """
    current_config = load_config(CONFIG_FILE)
    client = PgClient(current_config["default"])
    client.load(file, table, schema)


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database.
    """
