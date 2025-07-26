"""
Model interfaces & dataclasses.

Exports
-------
TrainResult  : light dataclass holding metrics & artefact paths
train_model  : stub that returns a TrainResult
"""

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class TrainResult:
    model_path: Path
    metrics: dict[str, float]


def train_model(df: pd.DataFrame) -> TrainResult:  # pragma: no cover
    """Placeholder training routine (returns dummy result)."""
    return TrainResult(Path("/tmp/dummy.pkl"), {"loss": 0.0})


# Backwards compatibility
train = train_model

from importlib import import_module


def update_unrealized_pnl(*args, **kwargs):  # pragma: no cover - thin wrapper
    return import_module("models.exit").update_unrealized_pnl(*args, **kwargs)


__all__ = ["TrainResult", "train_model", "train", "update_unrealized_pnl"]
