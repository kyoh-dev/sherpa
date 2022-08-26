from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from itertools import islice
from typing import Any

import fiona
from fiona import Collection
from tabulate import tabulate
from psycopg2.sql import SQL, Identifier
from psycopg2.extensions import parse_dsn
from psycopg2.extensions import connection as PgConnection
from psycopg2 import DatabaseError, ProgrammingError, connect

from sherpa.constants import console


@dataclass
class PgTable:
    name: str
    columns: list[str]


@dataclass
class PgRow:
    data: tuple[Any, ...]


@dataclass
class PgClient:
    dbname: str
    conn: PgConnection
    dsn: dict[str, str]

    def __init__(self, dsn: str) -> None:
        try:
            self.dsn = parse_dsn(dsn)
        except ProgrammingError:
            console.print("[cyan]sherpa:[/cyan] [bold red]error:[/bold red] invalid connection string")
            exit(1)

        self.dbname = self.dsn["dbname"]
        self.conn = self.pg_connect()

    def pg_connect(self) -> PgConnection:
        try:
            return connect(**self.dsn)
        except DatabaseError:
            console.print(
                f"[cyan]sherpa:[/cyan] [bold red]error:[/bold red] unable to connect to database {self.dbname}"
            )
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

        console.print(tabulate(results, headers=["SCHEMA", "TABLE"], tablefmt="psql"))
        self.conn.close()

    def get_table_info(self, table: str, schema: str = "public") -> PgTable:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                  AND table_name = %s
                ORDER BY column_name
                """,
                (schema, table),
            )
            results = cursor.fetchall()

        return PgTable(name=table, columns=[result for (result,) in results])

    def load(
        self,
        file: Path,
        table: str,
        schema: str = "public",
        batch_size: int = 1000,
    ) -> None:
        table_info = self.get_table_info(table, schema)
        with fiona.open(file, mode="r") as collection:
            fields = collection.schema["properties"].keys()
            if len(fields) > len(table_info.columns):
                console.print(
                    "[cyan]sherpa:[/cyan] [bold red]error:[/bold red] source contains more fields than target columns"
                )
                exit(1)

            row_generator = generate_rows(collection, table_info)

            finished = False
            while not finished:
                batch = islice(row_generator, 0, batch_size)
                if batch:
                    insert_cursor = self.conn.cursor()
                    transforms = ["%s"] * len(table_info.columns)
                    args = SQL(",").join(insert_cursor.mogrify(",".join(transforms), x) for x in list(batch))
                    statement = SQL(
                        """
                        INSERT INTO {}({})
                        VALUES ({})
                        """
                    ).format(Identifier(schema, table), SQL(",").join(Identifier(x) for x in table_info.columns), args)
                    insert_cursor.execute(statement)
                    console.log(f"Loaded {batch_size} rows")
                else:
                    finished = True
                    console.log(f"Finished loading")


def generate_rows(
    collection: Collection, table_info: PgTable, skip_empty_geoms: bool = True
) -> Generator[PgRow, None, None]:
    for record in collection:
        properties = record["properties"]
        geometry = record["geometry"]

        if skip_empty_geoms:
            if geometry is None:
                continue

        yield PgRow(data=(tuple(properties[col] for col in table_info.columns if col != "geometry") + (geometry,)))
