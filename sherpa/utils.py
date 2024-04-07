from typing import Optional

from tomlkit.toml_document import TOMLDocument

from sherpa.constants import DSN_FILE, CONSOLE
from sherpa.pg_client import PgClient, PgClientError


def format_error(msg: str) -> str:
    return f"[bold red]sherpa:[/bold red] {msg}"


def format_success(msg: str) -> str:
    return f"[bold green]sherpa:[/bold green] {msg}"


def format_info(msg: str) -> str:
    return f"[bold dodger_blue1]sherpa:[/bold dodger_blue1] {msg}"


def format_highlight(word: str) -> str:
    return f"[yellow1]{word}[/yellow1]"


def read_dsn_file() -> TOMLDocument:
    try:
        dsn_profile = DSN_FILE.read()
    except FileNotFoundError:
        CONSOLE.print(format_error("No DSN profile added yet. Run `sherpa dsn add` to add one."))
        exit(0)
    else:
        return dsn_profile


def get_pg_client(dsn_profile: dict[str, str]) -> Optional[PgClient]:
    try:
        client = PgClient(dsn_profile)
    except PgClientError as ex:
        CONSOLE.print(format_error(str(ex)))
        exit(1)
    else:
        return client
