"""Feature-engineering utilities.

Public API
----------
run_pipeline(df: pandas.DataFrame) -> pandas.DataFrame
"""

from importlib import import_module
from typing import Any, Callable
import pandas as pd


def _default_pipeline(df: pd.DataFrame) -> pd.DataFrame:  # noqa: D401
    """No-op placeholder pipeline."""
    return df


def _import_pipeline_module():
    for name in ("features_pipeline", "features.pipeline"):
        try:
            return import_module(name)
        except (ModuleNotFoundError, SystemExit):
            continue
    return None


def _load_pipeline() -> Callable[..., Any]:
    mod = _import_pipeline_module()
    if mod is None:
        return _default_pipeline
    return mod.run_pipeline  # type: ignore[attr-defined]


def run_pipeline(*args: Any, **kwargs: Any) -> Any:
    """Execute the user-provided feature pipeline if present."""
    return _load_pipeline()(*args, **kwargs)


def __getattr__(name: str) -> Any:
    if name in {"pipeline", "compute_features", "from_db"}:
        mod = _import_pipeline_module()
        if mod is None:
            raise AttributeError(name)
        if name == "pipeline":
            return mod
        return getattr(mod, name)
    raise AttributeError(name)


__all__ = ["run_pipeline", "pipeline", "compute_features", "from_db"]
