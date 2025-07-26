"""Report generation utilities and constants."""

from pathlib import Path
import os

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", Path(__file__).parent))

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
