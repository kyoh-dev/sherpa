from typing import Annotated

from typer import Typer, Argument

from sherpa.constants import CONSOLE
from sherpa.utils import read_dsn_file, format_error
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
        CONSOLE.print(format_error(f"No tables found in `{schema}`"))
    else:
        CONSOLE.print(table_info)

    client.close()


@app.callback()
def main() -> None:
    """
    Get info about tables in your PostGIS instance
    """
