from pathlib import Path
from typing import Annotated, Optional

from typer import Typer, Argument, Option
from psycopg2.errors import lookup
from fiona.crs import CRS, CRSError

from sherpa.constants import CONSOLE
from sherpa.utils import read_dsn_file, format_success, format_error, format_warning, format_highlight
from sherpa.database import get_pg_client

from sherpa.cmd import dsn
from sherpa.cmd import table

app = Typer(name="sherpa", no_args_is_help=True)
app.add_typer(dsn.app, name="dsn", no_args_is_help=True)
app.add_typer(table.app, name="table", no_args_is_help=True)


@app.command("load", no_args_is_help=True)
def load_file_to_pg(
    file: Annotated[Path, Argument(help="Path of the file to load", show_default=False)],
    table: Annotated[
        Optional[str], Argument(metavar="TEXT", help="Name of the table to load to", show_default=False)
    ] = None,
    schema: Annotated[
        str, Option("--schema", "-s", help="Schema of the table to load to", rich_help_panel="Database Options")
    ] = "public",
    create_table: Annotated[
        bool,
        Option(
            "--create",
            "-c",
            help="Create table by inferring the schema from the load file",
            rich_help_panel="Database Options",
        ),
    ] = False,
    srid: Annotated[
        Optional[int],
        Option(
            "--srid",
            "-i",
            help="Force geometries to an SRID on load (only supports EPSG codes)",
            rich_help_panel="Geometry Options",
        ),
    ] = None,
) -> None:
    """
    Load a file to a PostGIS table
    """
    table_name = table  # Avoid shadowing name from outer scope
    dsn_profile = read_dsn_file()

    if not file.exists():
        CONSOLE.print(format_error(f"File not found: {file}"))
        exit(1)

    if not table_name and create_table is False:
        CONSOLE.print(format_error("You must provide a table to load to or create one with --create/-c"))
        exit(1)

    if srid is not None:
        try:
            crs = CRS.from_epsg(srid)
        except CRSError as ex:
            CONSOLE.print(format_error(str(ex)))
            exit(1)
        else:
            srid = crs.to_epsg()
            CONSOLE.print(format_warning(f"Forcing geometries to EPSG:{srid}"), highlight=False)

    client = get_pg_client(dsn_profile["default"])

    if not client.schema_exists(schema):
        CONSOLE.print(format_error(f"Schema not found: {format_highlight(f'{schema}')}"))
        exit(1)

    if create_table:
        if table_name is None:
            create_table_name = file.name.removesuffix(file.suffix)
            CONSOLE.print(
                format_warning(f"Table name not provided, using file name {format_highlight(create_table_name)}")
            )
        else:
            create_table_name = table_name

        try:
            table_name = client.create_table(file, schema, create_table_name)
            CONSOLE.print(format_success(f"Created table {format_highlight(f'{schema}.{table_name}')}"))
        except lookup("42P07"):
            # Catch DuplicateTable errors
            CONSOLE.print(
                format_error(
                    f"Table {format_highlight(f'{schema}.{file.name.removesuffix(file.suffix)}')} already exists, use the --table/-t option instead"
                )
            )
            exit(1)

    table_structure = client.get_insert_table_info(table_name, schema)
    if not table_structure:
        CONSOLE.print(format_error(f"Table not found: {format_highlight(f'{schema}.{table_name}')}"))
        exit(1)

    rows_inserted = client.load(file, table_structure, force_srid=srid)
    client.close()

    CONSOLE.print(
        format_success(
            f"Loaded {rows_inserted} records to {format_highlight(f'{table_structure.schema}.{table_structure.table}')}"
        )
    )


@app.callback()
def main() -> None:
    """
    Load GIS files to a PostGIS database
    """
