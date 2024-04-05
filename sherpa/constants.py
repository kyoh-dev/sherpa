from pathlib import Path

from rich.console import Console

CONFIG_DIR = Path.home() / ".sherpa"
CONFIG_FILE = Path(CONFIG_DIR) / "config"

CONSOLE = Console()

# Maps Python data types to PG to infer table schema from a file
DATA_TYPE_MAP = {
    "str": "TEXT",
    "bool": "BOOLEAN",
    "int": "INTEGER",
    "float": "DOUBLE PRECISION",
}
