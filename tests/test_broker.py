"""Tests for broker API stub."""

import pandas as pd

from trading_platform import broker


def test_place_order(tmp_path):
    csv = tmp_path / "orders.csv"
    path = broker.place_order("AAPL", "BUY", 1, 100.0, out_file=str(csv))
    df = pd.read_csv(path)
    assert df.iloc[0]["symbol"] == "AAPL"
    assert df.iloc[0]["side"] == "BUY"
    assert df.iloc[0]["qty"] == 1
    assert df.iloc[0]["price"] == 100.0
