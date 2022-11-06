from pathlib import Path

from rich.console import Console

CONFIG_DIR = Path.home() / ".sherpa"
CONFIG_FILE = Path(CONFIG_DIR) / "config"

console = Console()
