"""Tests for paper trading simulator."""

import pandas as pd

from trading_platform import simulate


def test_simulate_buy_hold(tmp_path):
    csv = tmp_path / "feat.csv"
    csv.write_text("t,close\n1,1\n2,2\n3,3\n")
    sb = tmp_path / "score.csv"
    pf = tmp_path / "pf.csv"
    pnl = tmp_path / "pnl.csv"
    path = simulate.simulate(
        str(csv),
        capital=100.0,
        out_file=str(sb),
        portfolio_file=str(pf),
        pnl_file=str(pnl),
        symbol="AAA",
    )
    df = pd.read_csv(path)
    assert df.iloc[0]["pnl"] == 200.0
    assert not pf.exists() or pd.read_csv(pf).empty
    pnl_df = pd.read_csv(pnl)
    assert round(pnl_df.iloc[0]["realized"], 2) == 200.0
