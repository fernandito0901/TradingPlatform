import os
import pytest

os.environ.setdefault("POLYGON_API_KEY", "x")
os.environ.setdefault("NEWS_API_KEY", "x")

from trading_platform.collector import api


def test_helper_urls(monkeypatch):
    calls = []

    def fake_get(url, params=None):
        calls.append(url)
        return {"results": []}

    monkeypatch.setattr(api, "rate_limited_get", fake_get)

    api.fetch_prev_close("AAPL")
    with pytest.raises(api.NoData):
        api.fetch_open_close("AAPL", "2025-01-01")
    api.fetch_trades("AAPL", limit=10)
    api.fetch_quotes("AAPL", limit=10)
    api.fetch_snapshot_tickers()

    assert calls[0].endswith("/v2/aggs/ticker/AAPL/prev")
    assert "/v2/aggs/ticker/AAPL/range/1/day/2025-01-01/2025-01-01" in calls[1]
    assert calls[2].endswith("/v3/trades/AAPL")
    assert calls[3].endswith("/v3/quotes/AAPL")
    assert calls[4].endswith("/v2/snapshot/locale/us/markets/stocks/tickers")
