from pathlib import Path

from tomlkit.toml_file import TOMLFile
from rich.console import Console

CONFIG_DIR = Path.home() / ".sherpa"
CONFIG_FILE = Path(CONFIG_DIR) / "config.toml"

DSN_FILEPATH = Path(CONFIG_DIR) / "dsn.toml"
DSN_FILE = TOMLFile(DSN_FILEPATH)

CONSOLE = Console()

# Maps Python data types to PG to infer table schema from a file
DATA_TYPE_MAP = {
    "str": "TEXT",
    "bool": "BOOLEAN",
    "int": "INTEGER",
    "float": "DOUBLE PRECISION",
}
