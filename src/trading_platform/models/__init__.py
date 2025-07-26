"""Lazy access to the root ``models`` package."""

from importlib import import_module
from typing import Any


def train(*args: Any, **kwargs: Any):
    """Proxy to :func:`models.train.train`."""
    return import_module("models.train").train(*args, **kwargs)


def update_unrealized_pnl(*args: Any, **kwargs: Any):
    """Proxy to :func:`models.exit.update_unrealized_pnl`."""
    return import_module("models.exit").update_unrealized_pnl(*args, **kwargs)


TrainResult = import_module("models.train").TrainResult  # type: ignore[attr-defined]


__all__ = ["train", "update_unrealized_pnl", "TrainResult"]
