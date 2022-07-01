from collections.abc import Callable
from typing import TypeVar, Any, cast

import toml
from psycopg2 import ProgrammingError
from psycopg2.extensions import parse_dsn
from typer import Exit, echo, prompt

from sherpa.constants import CONFIG_FILE

F = TypeVar("F", bound=Callable[..., Any])


def check_config(fn: F) -> F:
    """
    Decorator to check whether a config file exists before executing a function.
    """

    def check() -> None:
        if CONFIG_FILE.exists():
            fn()
        else:
            echo("sherpa: error: config does not exist")
            Exit(1)

    return cast(F, check)


@check_config
def print_config() -> None:
    current_config = toml.load(CONFIG_FILE)
    for name, value in current_config["default"].items():
        echo(f"{name} = {value}", color=True)


def write_config() -> None:
    dsn = prompt("Postgres DSN")
    try:
        parsed_dsn = parse_dsn(dsn)
    except ProgrammingError:
        echo("sherpa: error: invalid connection string")
        Exit(1)
    else:
        default_config = {
            "default": {name: f'"{value}"' for name, value in parsed_dsn.items()},
        }
        default_config["default"]["dsn"] = f'"{dsn}"'
        with open(CONFIG_FILE, "w") as f:
            toml.dump(default_config, f)
