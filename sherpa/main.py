from typer import Typer

from sherpa.cmd import dsn
from sherpa.cmd import tables

app = Typer(name="sherpa", no_args_is_help=True)
app.add_typer(dsn.app, name="dsn", no_args_is_help=True)
app.add_typer(tables.app, name="tables", no_args_is_help=True)


# @app.command(name="tables")
# def list_tables(schema: str = Option("public", "--schema", "-s", help="Schema of tables to target")) -> None:
#     """
#     List tables in a specified schema (default: public)
#     """
#     current_config = load_config(CONFIG_FILE)
#     client = PgClient(current_config["default"])
#     table_info = client.list_table_counts(schema)
#     CONSOLE.print(table_info)
#     client.close()


# @app.command()
# def load(
#     file: Path = Argument(..., help="Path to file to load"),
#     table: str = Option("", "--table", "-t", help="Name of table to load to"),
#     schema: str = Option("public", "--schema", "-s", help="Schema of table to load to"),
#     create_table: bool = Option(
#         False,
#         "--create",
#         "-c",
#         help="Creates a table inferring the schema from the load file",
#     ),
# ) -> None:
#     """
#     Load a file to a PostGIS table
#     """
#     current_config = load_config(CONFIG_FILE)
#     client = PgClient(current_config["default"])
#     client.load(file, table, schema, create_table)
#     client.close()


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database.
    """
