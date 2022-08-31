import os
from pathlib import Path

from rich.console import Console

DEFAULT_CONFIG_DIR = Path.home() / ".sherpa"
CONFIG_DIR = os.environ.get("SHERPA_CONFIG_DIR", DEFAULT_CONFIG_DIR)
CONFIG_FILE = Path(CONFIG_DIR) / "config"

console = Console()
