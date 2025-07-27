"""Lazy feature pipeline exports."""

from importlib import import_module

__all__ = ["compute_features", "from_db", "run_pipeline"]


def __getattr__(name: str):
    if name in __all__:
        mod = import_module("features.pipeline")
        return getattr(mod, name)
    raise AttributeError(name)
