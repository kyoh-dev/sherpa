from typer import Typer, Option, Argument

from sherpa.constants import console, CONFIG_FILE
from sherpa.cmd_utils import load_config
from sherpa.pg_client import PgClient

app = Typer(name="info")


@app.command(name="tables")
def get_table_info(schema: str = Option("public", "--schema", "-s", help="Schema of tables to target")) -> None:
    """
    List tables in a specified schema (default: public)
    """
    current_config = load_config(CONFIG_FILE)
    client = PgClient(current_config["default"])
    table_info = client.list_tables(schema)
    console.print(table_info)


@app.command(name="count")
def get_table_count(table: str = Argument(..., help="Table to count with optional schema specifier")) -> None:
    """
    Count the rows in a table (format: schema.tables) (default: public)
    """
    table_ref = table.split(".")
    if len(table_ref) > 2:
        console.print(f"[bold red]Error: [/bold red]Cannot parse table reference: {table}")
    if len(table_ref) == 1:
        table_ref.insert(0, "public")

    current_config = load_config(CONFIG_FILE)
    client = PgClient(current_config["default"])
    count = client.get_table_count(table_ref[0], table_ref[1])
    if count is not None:
        console.print(
            f"Table [bold cyan]{table}[/bold cyan] currently holds [bold yellow]{count}[/bold yellow] records"
        )


@app.callback()
def main() -> None:
    """
    Get info about your PostGIS tables
    """
