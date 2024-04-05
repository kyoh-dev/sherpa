from typing import Annotated

import tomlkit
from typer import Typer, Argument

from sherpa.constants import DSN_FILEPATH, DSN_KEYS, CONFIG_DIR, CONSOLE
from sherpa.utils import format_highlight, format_success, format_error, read_dsn_file

app = Typer()


@app.command("ls")
def list_dsn_profile() -> None:
    """
    List DSN profile values
    """
    dsn_profile = read_dsn_file()

    for name, value in dsn_profile["default"].items():
        if name == "password":
            CONSOLE.print(
                f"{format_highlight(name)}={'*' * len(value)}",
                highlight=False,
            )
        else:
            CONSOLE.print(f"{format_highlight(name)}={value}", highlight=False)


@app.command("add")
def add_dsn_profile() -> None:
    """
    Add a DSN profile
    """
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir()

    profile_doc = tomlkit.document()
    default_profile = tomlkit.table()
    for x in ["user", "password", "dbname", "host", "port"]:
        dsn_value = CONSOLE.input(f"{format_highlight(x)}: ", password=True if x == "password" else False)
        default_profile.add(x, dsn_value)

    profile_doc.add("default", default_profile)
    with open(DSN_FILEPATH, "w") as f:
        tomlkit.dump(profile_doc, f)

    CONSOLE.print(format_success("DSN settings saved"))


@app.command("set")
def set_dsn_profile_value(
    key: Annotated[str, Argument(help=f"Update one of {DSN_KEYS}")],
    value: Annotated[str, Argument(help="Value to set the key to")],
) -> None:
    """
    Set a value for a key in your DSN profile
    """
    dsn_profile = read_dsn_file()

    try:
        dsn_profile["default"][key] = value
    except KeyError:
        CONSOLE.print(format_error(f"The DSN profile only uses the keys: {DSN_KEYS}"))
        exit(1)
    else:
        with open(DSN_FILEPATH, "w") as f:
            tomlkit.dump(dsn_profile, f)

        CONSOLE.print(format_success(f"{format_highlight(key)} updated in DSN profile"))


@app.callback()
def main() -> None:
    """
    Manage your DSN profile
    """
