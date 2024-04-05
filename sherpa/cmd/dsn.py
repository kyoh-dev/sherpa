import tomlkit
from typer import Typer

from sherpa.constants import DSN_FILE, CONFIG_DIR, CONSOLE
from sherpa.utils import format_highlight, format_success, read_dsn_file

app = Typer()


@app.command("list")
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
        dsn_value = CONSOLE.input(f"{format_highlight(x)}: ")
        default_profile.add(x, dsn_value)

    profile_doc.add("default", default_profile)
    with open(DSN_FILE, "w") as f:
        tomlkit.dump(profile_doc, f)

    CONSOLE.print(format_success("DSN settings saved"))


# @app.command("update")
# def update_dsn_profile(key: Annotated[str, Argument(help="Which part of the DSN to update")]) -> None:
#     """
#     Update a key within a DSN profile
#     """
#     dsn_profile = read_dsn_file()
#     ...
