import toml
from psycopg2 import ProgrammingError
from psycopg2.extensions import parse_dsn

from sherpa.constants import CONFIG_FILE, console


def load_config() -> dict[str, dict[str, str]]:
    if not CONFIG_FILE.exists():
        console.print("[bold red]Error:[/bold red] Config does not exist")
        exit(1)

    return toml.load(CONFIG_FILE)


def print_config() -> None:
    current_config = load_config()
    for name, value in current_config["default"].items():
        console.print(f"[yellow]{name}[/yellow]=[green]{value}[/green]", highlight=False)


def write_config() -> None:
    dsn = console.input("[bold]Postgres DSN[/bold]: ")
    try:
        parsed_dsn = parse_dsn(dsn)
    except ProgrammingError:
        console.print("[bold red]Error:[/bold red] Invalid connection string")
        exit(1)
    else:
        default_config = {
            "default": {name: f"{value}" for name, value in parsed_dsn.items()},
        }
        default_config["default"]["dsn"] = f"{dsn}"
        with open(CONFIG_FILE, "w") as f:
            toml.dump(default_config, f)

        console.print("[green]Config saved![/green]")
