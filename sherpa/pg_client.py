import json
from dataclasses import dataclass
from pathlib import Path
from itertools import islice
from collections.abc import Generator
from typing import Any

import fiona
from fiona import Collection
from rich.table import Table
from rich.progress import Progress
from psycopg2 import DatabaseError, connect
from psycopg2.sql import SQL, Identifier, Composed
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor

from sherpa.constants import console


@dataclass
class PgTable:
    name: str
    columns: list[str]

    @property
    def sql_composed_columns(self) -> Composed:
        return SQL(", ").join(Identifier(x) for x in self.columns)


@dataclass
class PgClient:
    conn: PgConnection

    def __init__(self, connection_details: dict[str, str]) -> None:
        try:
            self.conn = connect(**connection_details)
        except DatabaseError:
            console.print(f"[bold red]Error:[/bold red] Unable to connect to database [bold cyan]{connection_details['dbname']}[/bold cyan]")
            exit(1)

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def list_table_counts(self, schema: str = "public") -> Table:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  schemaname,
                  relname,
                  n_live_tup
                FROM pg_stat_user_tables
                WHERE schemaname = %s
                  AND relname <> 'spatial_ref_sys'
                ORDER BY relname
                """,
                (schema,),
            )
            results = cursor.fetchall()

        if len(results) == 0:
            console.print("[bold red]Error:[/bold red] schema not found")
            exit(1)

        table = Table("SCHEMA", "TABLE", "ROWS", style="cyan")
        for row in results:
            table.add_row(row[0], row[1], str(row[2]))

        return table

    def get_table_structure(self, table: str, schema: str = "public") -> PgTable:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name = %s
                  AND column_name <> %s
                """,
                (schema, table, "id"),
            )
            results = cursor.fetchall()

        if len(results) == 0:
            console.print(f"[bold red]Error:[/bold red] unable to get table structure for [bold cyan]{schema}.{table}[/bold cyan]")
            exit(1)

        return PgTable(name=table, columns=[result for (result,) in results])

    def load(self, file: Path, table: str, schema: str = "public", create_table: bool = False, batch_size: int = 10000) -> None:
        if not table and create_table is False:
            console.print("[bold red]Error:[/bold red] you must provide a table name or the --create option")
            exit(1)
        elif create_table:
            table = self.create_table_from_file(file, schema)

        table_info = self.get_table_structure(table, schema)
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            exit(1)

        with fiona.open(file, mode="r") as collection:
            row_generator = generate_row_data(collection, table_info)

            inserted = 0
            with Progress() as progress:
                load_task = progress.add_task(f"[cyan]Loading...[/cyan]", total=len(collection))
                while not progress.finished:
                    batch = list(islice(row_generator, 0, batch_size))
                    if batch:
                        insert_cursor = self.conn.cursor()
                        args_list = [generate_sql_insert_row(table_info, x, insert_cursor) for x in batch]
                        statement = SQL(
                            """
                            INSERT INTO {}({})
                            VALUES {}
                            RETURNING id;
                            """
                        ).format(Identifier(schema, table), table_info.sql_composed_columns, SQL(",").join(args_list))
                        insert_cursor.execute(statement)
                        inserted += len(insert_cursor.fetchall())
                        self.conn.commit()
                        progress.update(load_task, advance=len(batch))

            console.print(
                f"[green]Success:[/green] loaded [bold yellow]{inserted}[/bold yellow] records to [bold cyan]{schema}.{table}[/bold cyan]"
            )

    def create_table_from_file(self, file: Path, schema: str) -> str:
        with fiona.open(file, mode="r") as collection:
            columns = collection.schema["properties"]

        table_name = file.name.removesuffix(file.suffix)
        columns = [SQL("{} TEXT").format(Identifier(col)) for col in columns.keys()]
        q = SQL(
            """
            CREATE TABLE {table_name} (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                {columns},
                geometry GEOMETRY
            )
            """
        ).format(table_name=Identifier(schema, table_name), columns=SQL(", ").join(columns))

        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute(q)

        console.print(f"[green]Success:[/green] Created table [bold cyan]{schema}.{table_name}[/bold cyan]")
        return table_name


def generate_row_data(collection: Collection, table_info: PgTable) -> Generator[tuple[Any, ...], None, None]:
    for record in collection:
        properties = record["properties"]
        geometry = record["geometry"]

        yield tuple(properties[col] for col in table_info.columns if col != "geometry") + (json.dumps(geometry),)


def generate_sql_transforms(table_info: PgTable) -> list[str]:
    sql_transforms = ["%s" if x != "geometry" else "ST_GeomFromGeoJSON(%s)" for x in table_info.columns]
    return sql_transforms


def generate_sql_insert_row(table_info: PgTable, row_data: tuple[Any, ...], cursor: PgCursor) -> Composed:
    return SQL("({})").format(
        SQL(cursor.mogrify(",".join(generate_sql_transforms(table_info)), row_data).decode("utf-8"))
    )
