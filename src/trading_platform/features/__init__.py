"""Feature-engineering utilities.

Public API
----------
run_pipeline(df: pandas.DataFrame) -> pandas.DataFrame
"""

from importlib import import_module
from typing import Any


def load_pipeline(*args: Any, **kwargs: Any) -> Any:
    """Load and execute the user feature pipeline if available."""
    try:
        mod = import_module("features.pipeline")
        func = mod.run_pipeline  # type: ignore[attr-defined]
    except Exception:
        from .pipeline import run_pipeline as func
    return func(*args, **kwargs)


def run_pipeline(*args: Any, **kwargs: Any) -> Any:
    """Alias for :func:`load_pipeline`."""
    return load_pipeline(*args, **kwargs)


__all__ = ["load_pipeline", "run_pipeline"]
