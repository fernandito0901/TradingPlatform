"""Report generation utilities and constants."""

from pathlib import Path
import os

# Default to a writable reports directory under the current working directory.
# This allows Docker containers to mount the folder or override via
# ``REPORTS_DIR`` environment variable.
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", Path.cwd() / "reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

from .scoreboard import update_scoreboard
from .strategy_dashboard import generate_strategy_dashboard
from .dashboard import generate_dashboard
from .feature_dashboard import generate_feature_dashboard

__all__ = [
    "REPORTS_DIR",
    "update_scoreboard",
    "generate_strategy_dashboard",
    "generate_dashboard",
    "generate_feature_dashboard",
]
