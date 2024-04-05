from pathlib import Path
from typing import Annotated

from typer import Typer, Argument, Option
from psycopg2.errors import lookup

from sherpa.constants import CONSOLE
from sherpa.utils import read_dsn_file, format_error, format_highlight
from sherpa.pg_client import PgClient

from sherpa.cmd import dsn
from sherpa.cmd import tables

app = Typer(name="sherpa", no_args_is_help=True)
app.add_typer(dsn.app, name="dsn", no_args_is_help=True)
app.add_typer(tables.app, name="tables", no_args_is_help=True)


@app.command("load")
def load_file_to_pg(
    file: Annotated[Path, Argument(help="Path of the file to load")],
    table_name: Annotated[str, Option("--table", "-t", help="Name of the table to load to")] = None,
    schema_name: Annotated[str, Option("--schema", "-s", help="Schema of the table to load to")] = "public",
    create_table: Annotated[
        bool, Option("--create", "-c", help="Create table by inferring the schema from the load file")
    ] = False,
) -> None:
    """
    Load a file to a PostGIS table

    You can either specify an existing table to load to, or create one on the fly
    """
    dsn_profile = read_dsn_file()

    if not file.exists():
        CONSOLE.print(format_error(f"File not found: {file}"))
        exit(1)

    if not table_name and create_table is False:
        CONSOLE.print(format_error("You must either provide a table with --table/-t or the --create/-c option"))
        exit(1)

    client = PgClient(dsn_profile["default"])

    if create_table:
        try:
            table = client.create_table_from_file(file, schema_name)
        except lookup("42P07"):
            # Catch DuplicateTable errors
            CONSOLE.print(
                format_error(
                    f"Table {format_highlight(f'{schema_name}.{file.name.removesuffix(file.suffix)}')} already exists, use the --table/-t option instead"
                )
            )
            exit(1)
    else:
        table = table_name

    client.load(file, table, schema_name, create_table)

    client.close()


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database
    """
