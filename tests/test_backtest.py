import pandas as pd
import pytest

from models import train
from trading_platform import backtest


@pytest.mark.parametrize("days", [5, 10])
def test_backtest(tmp_path, days):
    dates = pd.date_range("2025-01-01", periods=40)
    df = pd.DataFrame(
        {
            "t": dates,
            "close": range(40),
            "sma20": range(40),
            "rsi14": range(40),
            "target": [0, 1] * 20,
        }
    )
    feat_csv = tmp_path / "features.csv"
    df.to_csv(feat_csv, index=False)
    model_dir = tmp_path / "models"
    res = train(str(feat_csv), model_dir=str(model_dir), symbol="T")
    pnl = tmp_path / "pnl.csv"
    path = backtest.backtest(
        str(feat_csv), res.model_path, days=days, out_file=str(pnl)
    )
    out_df = pd.read_csv(path)
    assert len(out_df) >= days
