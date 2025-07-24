"""Tests for model training utilities."""

import pandas as pd

from trading_platform.models import train as train_model


def test_train_model(tmp_path):
    data = {
        "sma20": [1, 2, 3, 4, 5, 6],
        "rsi14": [40, 50, 60, 55, 65, 70],
        "target": [0, 1, 0, 1, 0, 1],
    }
    df = pd.DataFrame(data)
    fpath = tmp_path / "features.csv"
    df.to_csv(fpath, index=False)
    model_path = tmp_path / "model.txt"
    train_auc, test_auc = train_model(str(fpath), str(model_path))
    assert 0.0 <= train_auc <= 1.0
    assert 0.0 <= test_auc <= 1.0
    assert model_path.exists()


def test_train_model_cv(tmp_path):
    data = {
        "sma20": list(range(1, 21)),
        "rsi14": list(range(20, 40)),
        "target": [0, 1] * 10,
    }
    df = pd.DataFrame(data)
    fpath = tmp_path / "features.csv"
    df.to_csv(fpath, index=False)
    model_path = tmp_path / "model.txt"
    mean_auc, _ = train_model(str(fpath), str(model_path), cv=True)
    assert 0.0 <= mean_auc <= 1.0
    assert model_path.exists()
