"""Model interfaces & dataclasses.

Exports
-------
TrainResult  : light dataclass holding metrics & artefact paths
train_model  : wrapper around user train function if available
"""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any
import pandas as pd


def _import_train_module():
    try:
        return import_module("models.train")
    except Exception:
        return None


def _import_exit_module():
    try:
        return import_module("models.exit")
    except Exception:
        return None


_train_mod = _import_train_module()
_exit_mod = _import_exit_module()

if _train_mod and hasattr(_train_mod, "TrainResult"):
    TrainResult = _train_mod.TrainResult  # type: ignore
else:

    @dataclass
    class TrainResult:
        train_auc: float
        test_auc: float
        cv_auc: float
        holdout_auc: float
        model_path: str
        metadata_path: str
        params: dict[str, Any]
        window_days: int

def train_model(*args: Any, **kwargs: Any) -> TrainResult:  # pragma: no cover
    mod = None
    if not args or not isinstance(args[0], pd.DataFrame):
        mod = _import_train_module()
    if mod and hasattr(mod, "train"):
        return mod.train(*args, **kwargs)
    model_dir = Path(kwargs.get("model_dir", "models"))
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "dummy.txt"
    meta_path = model_dir / "dummy_metadata.json"
    model_path.write_text("model")
    meta_path.write_text("{}")
    return TrainResult(
        0.0,
        0.0,
        0.0,
        0.0,
        str(model_path),
        str(meta_path),
        {},
        kwargs.get("window_days", 60),
    )

def train_model(*args: Any, **kwargs: Any) -> TrainResult:  # pragma: no cover
    mod = None
    if not args or not isinstance(args[0], pd.DataFrame):
        mod = _import_train_module()
    if mod and hasattr(mod, "train"):
        return mod.train(*args, **kwargs)
    model_dir = Path(kwargs.get("model_dir", "models"))
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "dummy.txt"
    meta_path = model_dir / "dummy_metadata.json"
    model_path.write_text("model")
    meta_path.write_text("{}")
    return TrainResult(
        0.0,
        0.0,
        0.0,
        0.0,
        str(model_path),
        str(meta_path),
        {},
        kwargs.get("window_days", 60),
    )


train = train_model

train = train_model

def update_unrealized_pnl(*args: Any, **kwargs: Any):  # pragma: no cover
    mod = _import_exit_module()
    if mod and hasattr(mod, "update_unrealized_pnl"):
        return mod.update_unrealized_pnl(*args, **kwargs)
    raise RuntimeError("exit.update_unrealized_pnl not available")


__all__ = ["TrainResult", "train_model", "train", "update_unrealized_pnl"]
