"""Feature pipeline entrypoint.

This package exposes ``load_pipeline`` which attempts to import
``features.pipeline`` and execute ``run_pipeline``. It mirrors the previous
``trading_platform.features`` wrapper so callers can simply invoke
``load_pipeline`` without knowing the implementation location.
"""

from importlib import import_module
from typing import Any

__all__ = ["load_pipeline", "run_pipeline", "compute_features", "from_db"]


def __getattr__(name: str):
    if name in __all__:
        mod = import_module("features.pipeline")
        return getattr(mod, name)
    raise AttributeError(name)


def load_pipeline(*args: Any, **kwargs: Any) -> Any:
    """Import and invoke ``run_pipeline`` from ``features.pipeline``."""
    mod = import_module("features.pipeline")
    func = getattr(mod, "run_pipeline")
    return func(*args, **kwargs)


def run_pipeline(*args: Any, **kwargs: Any) -> Any:
    """Alias for :func:`load_pipeline`."""
    return load_pipeline(*args, **kwargs)
