"""Environment variable loader."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def load_env(path: str | os.PathLike[str] = ".env") -> None:
    """Load environment variables from a ``.env`` file if it exists.

    Parameters
    ----------
    path : str or Path, optional
        File path to the ``.env`` file, by default ``".env"``.
    """
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def validate_env(required: Iterable[str]) -> None:
    """Ensure required variables are present."""
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
