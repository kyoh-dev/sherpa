from typing import Annotated

from rich.table import Table
from typer import Typer, Argument, Option

from sherpa.constants import CONSOLE
from sherpa.utils import read_dsn_file, format_error, format_highlight
from sherpa.database import get_pg_client

app = Typer()


@app.command("ls")
def list_tables(schema: Annotated[str, Option("--schema", "-s", help="Schema of tables to target")] = "public") -> None:
    """
    List tables and their row counts
    """
    dsn_profile = read_dsn_file()

    client = get_pg_client(dsn_profile["default"])

    if not client.schema_exists(schema):
        CONSOLE.print(format_error(f"Schema not found: {format_highlight(f'{schema}')}"))
        exit(1)

    table_counts = client.list_table_counts(schema)

    client.close()

    if not table_counts:
        CONSOLE.print(format_error(f"No tables found in schema {format_highlight(f'{schema}')}"))
        exit(1)

    console_table = Table("SCHEMA", "TABLE", "ROWS", style="cyan")
    for row in table_counts:
        console_table.add_row(row[0], row[1], str(row[2]))

    CONSOLE.print(console_table)


@app.command("shape")
def get_table_shape(
    table: Annotated[str, Argument(help="Name of the table", show_default=False)],
    schema: Annotated[str, Option("--schema", "-s", help="Schema of the table")] = "public",
) -> None:
    """
    Get the structure of a table
    """
    dsn_profile = read_dsn_file()

    client = get_pg_client(dsn_profile["default"])

    if not client.schema_exists(schema):
        CONSOLE.print(format_error(f"Schema not found: {format_highlight(f'{schema}')}"))
        exit(1)

    table_shape = client.get_table_shape(table, schema)

    client.close()

    if not table_shape:
        CONSOLE.print(format_error(f"Table not found: {format_highlight(f'{schema}.{table}')}"))
        exit(1)

    console_table = Table("COLUMN", "TYPE", "SRID", style="cyan")
    for row in table_shape:
        column_type = row[1] or row[2]
        srid = "" if row[3] is None else str(row[3])

        console_table.add_row(row[0], column_type.upper(), srid)

    CONSOLE.print(console_table)


@app.callback()
def main() -> None:
    """
    Get info about tables in your PostGIS instance
    """
