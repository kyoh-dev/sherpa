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
from psycopg2.sql import SQL, Identifier, Composed
from psycopg2.extensions import parse_dsn
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor
from psycopg2 import DatabaseError, ProgrammingError, connect

from sherpa.constants import console


@dataclass
class PgTable:
    name: str
    columns: list[str]

    @property
    def composed_columns(self) -> Composed:
        return SQL(", ").join(Identifier(x) for x in self.columns)


@dataclass
class PgClient:
    dbname: str
    conn: PgConnection
    dsn: dict[str, str]

    def __init__(self, dsn: str) -> None:
        try:
            self.dsn = parse_dsn(dsn)
        except ProgrammingError:
            console.print("[bold red]Error:[/bold red] Invalid connection string")
            exit(1)

        self.dbname = self.dsn["dbname"]
        self.conn = self.pg_connect()

    def pg_connect(self) -> PgConnection:
        try:
            return connect(**self.dsn)
        except DatabaseError:
            console.print(f'[bold red]Error:[/bold red] Unable to connect to database "{self.dbname}"')
            exit(1)

    def list_tables(self, schema: str = "public") -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  table_schema as schema,
                  table_name as table
                FROM information_schema.tables
                WHERE table_schema  = %s
                  AND table_type <> 'VIEW'
                  AND table_name <> 'spatial_ref_sys'
                ORDER BY table_name
                """,
                (schema,),
            )
            results = cursor.fetchall()

        table = Table()
        table.add_column("SCHEMA", style="cyan")
        table.add_column("TABLE")
        for row in results:
            table.add_row(row[0], row[1])
        console.print(table)

        self.conn.close()

    def get_table_info(self, table: str, schema: str = "public") -> PgTable:
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

        return PgTable(name=table, columns=[result for (result,) in results])

    def load(self, file: Path, table: str, schema: str = "public", batch_size: int = 1000) -> None:
        table_info = self.get_table_info(table, schema)
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            exit(1)

        with fiona.open(file, mode="r") as collection:
            fields = collection.schema["properties"].keys()
            if len(fields) > len(table_info.columns):
                console.print("[bold red]Error:[/bold red] Source contains more fields than target columns")
                exit(1)

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
                        ).format(Identifier(schema, table), table_info.composed_columns, SQL(",").join(args_list))
                        insert_cursor.execute(statement)
                        inserted += len(insert_cursor.fetchall())
                        self.conn.commit()
                        progress.update(load_task, advance=len(batch))

            console.log(
                f"[green]Successfully loaded [/green][bold yellow]{inserted}[/bold yellow] [green]records[/green]"
            )

        self.conn.close()


def generate_row_data(
    collection: Collection, table_info: PgTable, skip_empty_geoms: bool = True
) -> Generator[tuple[Any, ...], None, None]:
    for record in collection:
        properties = record["properties"]
        geometry = record["geometry"]

        if skip_empty_geoms:
            if geometry is None:
                continue

        yield tuple(properties[col] for col in table_info.columns if col != "geometry") + (json.dumps(geometry),)


def generate_sql_transforms(table_info: PgTable) -> list[str]:
    sql_transforms = ["%s" if x != "geometry" else "ST_GeomFromGeoJSON(%s)" for x in table_info.columns]
    return sql_transforms


def generate_sql_insert_row(table_info: PgTable, row_data: tuple[Any, ...], cursor: PgCursor) -> Composed:
    return SQL("({})").format(
        SQL(cursor.mogrify(",".join(generate_sql_transforms(table_info)), row_data).decode("utf-8"))
    )
