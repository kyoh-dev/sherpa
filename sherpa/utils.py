from pathlib import Path
from typing import Any

import toml

from sherpa.constants import CONSOLE


def load_config(file: Path) -> dict[str, dict[str, str]]:
    if not file.exists():
        CONSOLE.print("[bold red]Error:[/bold red] Config does not exist")
        exit(1)

    return toml.load(file)


def print_config(file: Path) -> None:
    current_config = load_config(file)
    for name, value in current_config["default"].items():
        if name == "password":
            CONSOLE.print(
                f"[yellow]{name}[/yellow]=[green]{'*' * len(value)}[/green]",
                highlight=False,
            )
        else:
            CONSOLE.print(f"[yellow]{name}[/yellow]=[green]{value}[/green]", highlight=False)


def write_config(file: Path, dsn: dict[str, Any]) -> None:
    if not file.exists():
        file.parent.mkdir(exist_ok=True)

    default_config = {
        "default": {name: f"{value}" for name, value in dsn.items()},
    }
    with open(file, "w") as f:
        toml.dump(default_config, f)

    CONSOLE.print("[green]Config saved![/green]")
