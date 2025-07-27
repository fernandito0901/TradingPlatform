"""Report generation utilities and constants."""

from pathlib import Path
import os

# Default to a writable reports directory. When ``REPORTS_DIR`` is not provided,
# fallback to ``./reports`` relative to the current working directory so docker
# containers can always write there regardless of install location.
_DEFAULT_DIR = Path.cwd() / "reports"
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", _DEFAULT_DIR))
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
