from typing import Optional

from typer import Option, Typer, Exit, echo, prompt

from sherpa.constants import CONFIG_FILE

app = Typer(name="sherpa")


@app.command()
def config(
    profile: Optional[str] = Option("default", "--profile", "-p", help="configuration profile"),
    list_all: Optional[bool] = Option(False, "--list-all", "-l", help="list all config options"),
) -> None:
    """
    Get and set configuration options
    """
    if list_all:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                echo(f"{f.read()}\n")
        else:
            echo("error: config does not exist")
            Exit(code=1)
    else:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.parent.mkdir(exist_ok=True)

        dsn = prompt("Postgres DSN")
        with open(CONFIG_FILE, "w") as f:
            f.writelines([f"[{profile}]\n", f"dsn = {dsn}"])


@app.callback()
def main() -> None:
    """
    A CLI tool for loading GIS files to a PostGIS database.
    """
