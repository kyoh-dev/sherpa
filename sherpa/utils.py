from collections.abc import Callable
from typing import TypeVar, Any, cast

import toml
from psycopg2 import ProgrammingError
from psycopg2.extensions import parse_dsn
from typer import prompt

from sherpa.constants import CONFIG_FILE, console

F = TypeVar("F", bound=Callable[..., Any])


def check_config(fn: F) -> F:
    """
    Decorator to check whether a config file exists before executing a function.
    """
    def check() -> None:
        if CONFIG_FILE.exists():
            fn()
        else:
            console.print("[cyan]sherpa:[/cyan] [bold red]error:[/bold red] config does not exist")
            exit(1)

    return cast(F, check)


@check_config
def print_config() -> None:
    current_config = toml.load(CONFIG_FILE)
    for name, value in current_config["default"].items():
        console.print(f"[yellow]{name}[/yellow]=[green]{value}[/green]", highlight=False)


def write_config() -> None:
    dsn = prompt("Postgres DSN")
    try:
        parsed_dsn = parse_dsn(dsn)
    except ProgrammingError:
        console.print("[cyan]sherpa:[/cyan] [bold red]error:[/bold red] invalid connection string")
        exit(1)
    else:
        default_config = {
            "default": {name: f"{value}" for name, value in parsed_dsn.items()},
        }
        default_config["default"]["dsn"] = f"{dsn}"
        with open(CONFIG_FILE, "w") as f:
            toml.dump(default_config, f)
