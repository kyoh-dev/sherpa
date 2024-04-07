from typing import Optional

from sherpa.constants import CONSOLE
from sherpa.pg_client import PgClient, PgClientError
from sherpa.utils import format_error


def get_pg_client(dsn_profile: dict[str, str]) -> Optional[PgClient]:
    try:
        client = PgClient(dsn_profile)
    except PgClientError as ex:
        CONSOLE.print(format_error(str(ex)))
        exit(1)
    else:
        return client
