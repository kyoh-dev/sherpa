from typing import Annotated

from rich.table import Table
from typer import Typer, Argument, Option

from sherpa.constants import CONSOLE
from sherpa.utils import read_dsn_file, format_error, format_highlight
from sherpa.pg_client import PgClient

app = Typer()


@app.command("ls")
def list_tables(schema: Annotated[str, Argument(help="Schema of tables to target")] = "public") -> None:
    """
    List tables and their row counts in a specified schema
    """
    dsn_profile = read_dsn_file()

    client = PgClient(dsn_profile["default"])
    table_info = client.list_table_counts(schema)

    if not table_info:
        CONSOLE.print(format_error(f"No tables found in schema `{schema}`"))
    else:
        CONSOLE.print(table_info)

    client.close()


@app.command("shape")
def get_table_shape(
    table: Annotated[str, Argument(help="Name of the table", show_default=False)],
    schema: Annotated[str, Option("--schema", "-s", help="Schema of the table")] = "public",
) -> None:
    """
    Get the structure of a table in a specified schema
    """
    dsn_profile = read_dsn_file()

    client = PgClient(dsn_profile["default"])
    table_shape = client.get_table_shape(table, schema)

    if not table_shape:
        CONSOLE.print(format_error(f"Table not found: {format_highlight(f'{schema}.{table}')}"))
        exit(1)

    console_table = Table("COLUMN", "TYPE", "SRID", style="cyan")
    for row in table_shape:
        console_table.add_row(row[0], row[1] or row[2], str(row[3]))

    CONSOLE.print(console_table)


@app.callback()
def main() -> None:
    """
    Get info about tables in your PostGIS instance
    """
