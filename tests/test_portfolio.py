"""Tests for portfolio tracker."""

import pandas as pd

from trading_platform import portfolio


def test_record_and_close(tmp_path):
    pf = tmp_path / "pf.csv"
    pnl = tmp_path / "pnl.csv"
    portfolio.record_trade("AAPL", "buy_hold", 1, 100.0, portfolio_file=str(pf))
    df = pd.read_csv(pf)
    assert df.iloc[0]["symbol"] == "AAPL"
    assert df.iloc[0]["qty"] == 1
    portfolio.close_position("AAPL", 110.0, portfolio_file=str(pf), pnl_file=str(pnl))
    df = pd.read_csv(pf)
    assert df.empty
    pnl_df = pd.read_csv(pnl)
    assert round(pnl_df.iloc[0]["realized"], 2) == 10.0
