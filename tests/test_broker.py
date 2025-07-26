"""Tests for broker API stub."""

import pandas as pd

from trading_platform import broker


def test_place_order(tmp_path):
    csv = tmp_path / "orders.csv"
    pf = tmp_path / "pf.csv"
    path = broker.place_order(
        "AAPL", "BUY", 1, 100.0, out_file=str(csv), portfolio_file=str(pf)
    )
    df = pd.read_csv(path)
    assert df.iloc[0]["symbol"] == "AAPL"
    assert df.iloc[0]["side"] == "BUY"
    assert df.iloc[0]["qty"] == 1
    assert df.iloc[0]["price"] == 100.0
    portfolio_df = pd.read_csv(pf)
    assert portfolio_df.iloc[0]["symbol"] == "AAPL"
    assert portfolio_df.iloc[0]["qty"] == 1


def test_place_order_alpaca(monkeypatch, tmp_path):
    csv = tmp_path / "orders.csv"
    pf = tmp_path / "pf.csv"

    called = {}

    def fake_post(url, json=None, headers=None, timeout=5):
        called["url"] = url

        class Resp:
            def raise_for_status(self):
                pass

        return Resp()

    monkeypatch.setenv("BROKER_URL", "https://paper.example")
    monkeypatch.setenv("APCA_KEY", "k")
    monkeypatch.setenv("APCA_SECRET", "s")
    monkeypatch.setattr(broker.requests, "post", fake_post)

    broker.place_order(
        "MSFT",
        "SELL",
        2,
        200.0,
        out_file=str(csv),
        portfolio_file=str(pf),
    )

    assert called["url"].endswith("/v2/orders")
