from pathlib import Path
from typing import Annotated

from typer import Typer, Argument, Option
from psycopg2.errors import lookup

from sherpa.constants import CONSOLE
from sherpa.utils import read_dsn_file, format_success, format_error, format_highlight
from sherpa.pg_client import PgClient, PgClientError

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

    try:
        client = PgClient(dsn_profile["default"])
    except PgClientError as ex:
        CONSOLE.print(format_error(str(ex)))
        exit(1)

    if not client.schema_exists(schema_name):
        CONSOLE.print(format_error(f"Schema {format_highlight(f'{schema_name}')} needs to exist already"))
        exit(1)

    if create_table:
        try:
            table_name = client.create_table_from_file(file, schema_name)
            CONSOLE.print(format_success(f"Created table {format_highlight(f'{schema_name}.{table_name}')}"))
        except lookup("42P07"):
            # Catch DuplicateTable errors
            CONSOLE.print(
                format_error(
                    f"Table {format_highlight(f'{schema_name}.{file.name.removesuffix(file.suffix)}')} already exists, use the --table/-t option instead"
                )
            )
            exit(1)

    table_info = client.get_table_structure(table_name, schema_name)
    if not table_info:
        CONSOLE.print(
            format_error(f"Unable to get table structure for {format_highlight(f'{schema_name}.{table_name}')}")
        )
        exit(1)

    rows_inserted = client.load(file, table_info, create_table)
    client.close()

    CONSOLE.print(
        format_success(
            f"Loaded {rows_inserted} records to {format_highlight(f'{table_info.schema}.{table_info.table}')}"
        )
    )


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database
    """
