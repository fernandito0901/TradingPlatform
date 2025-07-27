from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class TrainResult:
    model_path: Path
    metrics: dict[str, float]


def train(df: pd.DataFrame) -> TrainResult:  # pragma: no cover
    """Placeholder training routine."""
    return TrainResult(Path("/tmp/dummy.pkl"), {"loss": 0.0})
