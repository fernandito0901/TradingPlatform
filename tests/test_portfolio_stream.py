import importlib
import json

import pandas as pd
import pytest

from trading_platform.collector import portfolio_stream, stream_async, db


class FakeWS:
    def __init__(self, url, urls):
        self.url = url
        self.urls = urls
        self.urls.append(url)
        self.messages = [json.dumps([{"ev": "T", "sym": "AAPL", "p": 101, "t": 1}])]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def send(self, msg):
        pass

    def __aiter__(self):
        async def gen():
            for m in self.messages:
                yield m

        return gen()

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_stream_portfolio_quotes(monkeypatch, tmp_path):
    importlib.reload(portfolio_stream)
    importlib.reload(stream_async)

    pf = tmp_path / "portfolio.csv"
    pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "strategy": "s",
                "qty": 1,
                "avg_price": 100,
                "opened_at": "0",
            }
        ]
    ).to_csv(pf, index=False)

    urls = []

    def fake_connect(url):
        return FakeWS(url, urls)

    monkeypatch.setattr(
        stream_async, "websockets", type("W", (), {"connect": fake_connect})
    )

    conn = db.init_db(":memory:")
    await portfolio_stream.stream_portfolio_quotes(conn, str(pf))

    row = conn.execute("SELECT symbol, price FROM realtime_quotes").fetchone()
    assert row == ("AAPL", 101)
    assert urls == [stream_async.WS_URL]
