import json
from dataclasses import dataclass
from pathlib import Path
from itertools import islice
from collections.abc import Generator
from typing import Any, Optional

import fiona
from fiona import Collection
from rich.table import Table
from rich.progress import Progress
from psycopg2 import DatabaseError, ProgrammingError, connect, errors
from psycopg2.sql import SQL, Identifier, Composed
from psycopg2.extensions import parse_dsn, connection as PgConnection, cursor as PgCursor

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
    conn: PgConnection

    def __init__(self, connection_details: dict[str, str]) -> None:
        try:
            self.conn = connect(**connection_details)
        except DatabaseError:
            console.print(f"[bold red]Error:[/bold red] Unable to connect to database `{connection_details['dbname']}`")
            exit(1)

    def list_tables(self, schema: str = "public") -> Table:
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

        self.conn.close()
        return table

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

    def get_table_count(self, schema: str, table: str) -> Optional[int]:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    SQL(
                        """
                    SELECT COUNT(*)
                    FROM {}
                    """
                    ).format(Identifier(schema, table))
                )
                return int(cursor.fetchone()[0])
        except errors.lookup("42P01"):
            console.print("[bold red]Error:[/bold red] Undefined table or schema")
            return None
        finally:
            self.conn.close()

    def load(self, file: Path, table: str, schema: str = "public", batch_size: int = 10000) -> None:
        table_info = self.get_table_info(table, schema)
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
                        ).format(Identifier(schema, table), table_info.composed_columns, SQL(",").join(args_list))
                        insert_cursor.execute(statement)
                        inserted += len(insert_cursor.fetchall())
                        self.conn.commit()
                        progress.update(load_task, advance=len(batch))

            console.print(
                f"[green]Successfully loaded [/green][bold yellow]{inserted}[/bold yellow] [green]records[/green]"
            )

        self.conn.close()


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
