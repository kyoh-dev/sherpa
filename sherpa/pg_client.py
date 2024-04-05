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
from psycopg2 import DatabaseError, connect
from psycopg2.sql import SQL, Identifier, Composed
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor

from sherpa.constants import CONSOLE, DATA_TYPE_MAP
from sherpa.utils import format_error, format_highlight


@dataclass
class PgTable:
    schema: str
    table: str
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
            dbname = connection_details["dbname"]
            CONSOLE.print(format_error(f"Unable to connect to database {format_highlight(f'{dbname}')}"))
            exit(1)

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def list_table_counts(self, schema: str = "public") -> Optional[Table]:
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
            return None

        table = Table("SCHEMA", "TABLE", "ROWS", style="cyan")
        for row in results:
            table.add_row(row[0], row[1], str(row[2]))

        return table

    def get_table_structure(self, table: str, schema: str = "public") -> Optional[PgTable]:
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
            return None

        return PgTable(schema=schema, table=table, columns=[result for (result,) in results])

    def schema_exists(self, schema: str) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name = %s
                """,
                (schema,),
            )
            results = cursor.fetchone()

        return True if results else False

    def load(
        self,
        file: Path,
        table_info: PgTable,
        batch_size: int = 10000,
    ) -> int:
        with fiona.open(file, mode="r") as collection:
            row_generator = generate_row_data(collection, table_info)

            inserted = 0
            with Progress() as progress:
                load_task = progress.add_task("[cyan]Loading...[/cyan]", total=len(collection))
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
                        ).format(
                            Identifier(table_info.schema, table_info.table),
                            table_info.sql_composed_columns,
                            SQL(",").join(args_list),
                        )
                        insert_cursor.execute(statement)
                        inserted += len(insert_cursor.fetchall())
                        self.conn.commit()
                        progress.update(load_task, advance=len(batch))

        return inserted

    def create_table_from_file(self, file: Path, schema: str) -> str:
        with fiona.open(file, mode="r") as collection:
            file_schema = collection.schema["properties"]

        table_name = file.name.removesuffix(file.suffix)
        columns = list(file_schema.items())
        fields = [SQL("{} {}").format(Identifier(col[0]), SQL(DATA_TYPE_MAP[col[1]])) for col in columns]
        q = SQL(
            """
            CREATE TABLE {} (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                {},
                geometry GEOMETRY
            )
            """,
        ).format(Identifier(schema, table_name), SQL(",").join(fields))

        with self.conn.cusror() as cursor:
            cursor.execute(q)
            self.conn.commit()

        return table_name


def generate_row_data(collection: Collection, table_info: PgTable) -> Generator[tuple[Any, ...], None, None]:
    for record in collection:
        properties = record["properties"]
        geometry = {
            "type": record["geometry"]["type"],
            "coordinates": record["geometry"]["coordinates"],
        }

        yield tuple(properties[col] for col in table_info.columns if col != "geometry") + (json.dumps(geometry),)


def generate_sql_transforms(table_info: PgTable) -> list[str]:
    sql_transforms = ["%s" if x != "geometry" else "ST_GeomFromGeoJSON(%s)" for x in table_info.columns]
    return sql_transforms


def generate_sql_insert_row(table_info: PgTable, row_data: tuple[Any, ...], cursor: PgCursor) -> Composed:
    return SQL("({})").format(
        SQL(cursor.mogrify(",".join(generate_sql_transforms(table_info)), row_data).decode("utf-8"))
    )
