"""Report generation utilities and constants."""

from pathlib import Path
import os

# Default to a writable reports directory outside the package source. When no
# ``REPORTS_DIR`` environment variable is provided we resolve the repository
# root (three parents up from this file) and place a ``reports`` folder there.
_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "reports"
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
