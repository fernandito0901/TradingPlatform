"""Tests for model training utilities."""

from pathlib import Path

import pandas as pd

from models import TrainResult
from models import train as train_model


def test_train_model(tmp_path):
    data = {
        "t": pd.date_range("2025-01-01", periods=12),
        "sma20": list(range(12)),
        "rsi14": list(range(12, 24)),
        "target": [0, 1] * 6,
    }
    df = pd.DataFrame(data)
    fpath = tmp_path / "features.csv"
    df.to_csv(fpath, index=False)
    res = train_model(str(fpath), model_dir=str(tmp_path), symbol="A")
    assert isinstance(res, TrainResult)
    assert 0.0 <= res.train_auc <= 1.0
    assert 0.0 <= res.test_auc <= 1.0
    assert Path(res.model_path).exists()


def test_train_model_cv(tmp_path):
    data = {
        "t": pd.date_range("2025-01-01", periods=20),
        "sma20": list(range(1, 21)),
        "rsi14": list(range(20, 40)),
        "target": [0, 1] * 10,
    }
    df = pd.DataFrame(data)
    fpath = tmp_path / "features.csv"
    df.to_csv(fpath, index=False)
    res = train_model(str(fpath), model_dir=str(tmp_path), cv=True, symbol="B")
    assert 0.0 <= res.cv_auc <= 1.0
    assert Path(res.model_path).exists()


def test_train_window_filter(tmp_path):
    dates = pd.date_range("2025-01-01", periods=100)
    df = pd.DataFrame(
        {"t": dates, "sma20": range(100), "rsi14": range(100), "target": [0, 1] * 50}
    )
    fpath = tmp_path / "f.csv"
    df.to_csv(fpath, index=False)
    res = train_model(str(fpath), model_dir=str(tmp_path), window_days=30, symbol="C")
    assert res.window_days == 30
    assert Path(res.model_path).exists()
