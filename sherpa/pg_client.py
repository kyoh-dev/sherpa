import json
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Generator
from typing import Any, Optional, Union

import fiona
from fiona import Collection
from rich.progress import Progress
from psycopg2 import DatabaseError, connect
from psycopg2.sql import SQL, Identifier, Composed
from psycopg2.extensions import connection as PgConnection, cursor as PgCursor

from sherpa.constants import DATA_TYPE_MAP


class PgClientError(Exception):
    """
    Raise when an error occurs in a PgClient instance or operation
    """


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
            raise PgClientError(f"Unable to connect to database `{connection_details['dbname']}`")

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def list_table_counts(self, schema: str = "public") -> Optional[list[tuple[Union[str, int], ...]]]:
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

        return list(results)

    def get_insert_table_info(self, table: str, schema: str = "public") -> Optional[PgTable]:
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

    def get_table_shape(self, table: str, schema: str = "public") -> Optional[list[tuple[Union[str, int], ...]]]:
        with self.conn.cursor() as cursor:
            # NB: This can probably be optimised, 2 sub-queries is not ideal
            cursor.execute(
                """
                SELECT
                    info_schema.column_name,
                    CASE
                        WHEN info_schema.data_type = 'USER-DEFINED' THEN NULL
                        ELSE info_schema.data_type
                    END AS data_type,
                    (
                        SELECT geometry.type
                        FROM geometry_columns AS geometry
                        WHERE info_schema.table_schema = geometry.f_table_schema
                            AND info_schema.table_name = geometry.f_table_name
                            AND (info_schema.udt_name = 'geometry' OR info_schema.udt_name = 'geography')
                    ) AS geometry_type,
                    (
                        SELECT geometry.srid
                        FROM geometry_columns AS geometry
                        WHERE info_schema.table_schema = geometry.f_table_schema
                            AND info_schema.table_name = geometry.f_table_name
                            AND (info_schema.udt_name = 'geometry' OR info_schema.udt_name = 'geography')
                    ) AS srid
                FROM information_schema.columns AS info_schema
                WHERE info_schema.table_schema = %s
                    AND info_schema.table_name = %s;
                """,
                (schema, table),
            )
            results = cursor.fetchall()

        if len(results) == 0:
            return None

        return list(results)

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
        table_structure: PgTable,
        batch_size: int = 10000,
    ) -> int:
        with fiona.open(file, mode="r") as collection:
            rows = list(generate_row_data(collection, table_structure))
            inserted = 0
            with Progress() as progress:
                load_task = progress.add_task("[cyan]Loading...[/cyan]", total=len(collection))
                while not progress.finished:
                    # NB: If this gets to be a problem with large files
                    # go back to using islice iterator
                    batch = rows[inserted : batch_size + inserted]
                    if batch:
                        insert_cursor = self.conn.cursor()
                        args_list = [generate_sql_insert_row(table_structure, x, insert_cursor) for x in batch]
                        statement = SQL(
                            """
                            INSERT INTO {}({})
                            VALUES {}
                            RETURNING id;
                            """
                        ).format(
                            Identifier(table_structure.schema, table_structure.table),
                            table_structure.sql_composed_columns,
                            SQL(",").join(args_list),
                        )
                        insert_cursor.execute(statement)
                        inserted += len(insert_cursor.fetchall())
                        self.conn.commit()
                        progress.update(load_task, advance=len(batch))

            return inserted

    def create_table(self, file: Path, schema: str, table_name: str) -> str:
        with fiona.open(file, mode="r") as collection:
            file_schema = collection.schema["properties"]

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

        with self.conn.cursor() as cursor:
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
