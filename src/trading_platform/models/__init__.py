
"""Model interfaces & dataclasses."""

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

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


@dataclass
class TrainResult:
    """Simple training result container."""


    model_path: Path
    metrics: dict[str, float]


def train_model(df: pd.DataFrame) -> TrainResult:  # pragma: no cover
    """Placeholder training routine (returns dummy result)."""
    return TrainResult(Path("/tmp/dummy.pkl"), {"loss": 0.0})
