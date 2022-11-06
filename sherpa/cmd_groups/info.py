from typer import Option, Typer

from sherpa.constants import console, CONFIG_FILE
from sherpa.utils import load_config
from sherpa.pg_client import PgClient

app = Typer(name="info")


@app.command(name="tables")
def get_table_info(schema: str = Option("public", "--schema", "-s", help="Schema of tables to target")) -> None:
    """
    List tables in a specified schema (default: public)
    """
    current_config = load_config(CONFIG_FILE)
    client = PgClient(current_config["default"])
    table_info = client.list_table_counts(schema)
    console.print(table_info)


@app.callback()
def main() -> None:
    """
    Get info about your PostGIS tables
    """
