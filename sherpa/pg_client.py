from dataclasses import dataclass

from tabulate import tabulate
from psycopg2.extensions import parse_dsn
from psycopg2.extensions import connection as PgConnection
from psycopg2 import DatabaseError, ProgrammingError, connect


@dataclass
class PgClient:
    dbname: str
    conn: PgConnection
    dsn: dict[str, str]

    def __init__(self, dsn: str) -> None:
        try:
            self.dsn = parse_dsn(dsn)
        except ProgrammingError:
            exit("sherpa: invalid connection string")

        self.dbname = self.dsn["dbname"]
        self.conn = self.pg_connect()

    def pg_connect(self) -> PgConnection:
        try:
            print(f"sherpa: attempting to connect to: {self.dbname}")
            return connect(**self.dsn)
        except DatabaseError:
            exit("sherpa: unable to connect to database")

    def list_tables(self) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                  table_schema as schema,
                  table_name as table
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'tiger', 'topology')
                  AND table_type <> 'VIEW'
                  AND table_name <> 'spatial_ref_sys'
                  AND is_insertable_into = 'YES'
                """
            )
            results = cursor.fetchall()

        print(tabulate(results, tablefmt="psql"))
