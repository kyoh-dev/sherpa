from dataclasses import dataclass
from typing import Optional, Any

import questionary
from psycopg2.extensions import parse_dsn
from psycopg2.extensions import connection
from psycopg2 import connect, ProgrammingError, DatabaseError

from .questions import enter_dsn
from .errors import ExitedError


@dataclass
class PgClient:
    dbname: str
    user: str
    password: str
    host: str
    port: Optional[str]
    _dsn: dict[str, Any]

    def __init__(self) -> None:
        self._dsn = questionary.prompt([enter_dsn])
        if not self._dsn:
            raise ExitedError()

        self.dbname = self.dsn["dbname"]
        self.user = self.dsn["user"]
        self.password = self.dsn["password"]
        self.host = self.dsn["host"]
        self.port = self.dsn.get("port", "5432")

    def pg_connect(self) -> connection:
        try:
            return connect(self.dsn)
        except DatabaseError:
            raise ExitedError()

    @property
    def dsn(self) -> Any:
        try:
            return parse_dsn(self._dsn.get("dsn"))
        except ProgrammingError:
            raise ExitedError()
