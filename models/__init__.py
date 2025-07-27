"""Model training utilities."""

import tempfile
from pathlib import Path

import pandas as pd

from .train import TrainResult, train


def train_model(data: pd.DataFrame | str, **kwargs) -> TrainResult:
    """Train model from a DataFrame or CSV path."""

    if isinstance(data, pd.DataFrame):
        if data.empty:
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
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        data.to_csv(tmp.name, index=False)
        path = tmp.name
    else:
        path = data
    return train(path, **kwargs)


from .exit import update_unrealized_pnl

__all__ = ["train", "train_model", "TrainResult", "update_unrealized_pnl"]
