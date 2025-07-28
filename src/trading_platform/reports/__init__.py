"""Report generation utilities and constants."""

import os
import tempfile
from pathlib import Path

# Default to a writable reports directory. When ``REPORTS_DIR`` is not provided,
# fallback to ``/app/data/reports`` so Docker containers can always write there
# regardless of the working directory or install location.
_DEFAULT = Path("/app/data/reports")
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", _DEFAULT))
try:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:  # pragma: no cover - read-only FS
    tmp = Path(tempfile.mkdtemp(prefix="reports_"))
    REPORTS_DIR = tmp  # noqa: PLW0603

from .dashboard import generate_dashboard
from .feature_dashboard import generate_feature_dashboard
from .scoreboard import update_scoreboard
from .strategy_dashboard import generate_strategy_dashboard

__all__ = [
    "REPORTS_DIR",
    "update_scoreboard",
    "generate_strategy_dashboard",
    "generate_dashboard",
    "generate_feature_dashboard",
]
