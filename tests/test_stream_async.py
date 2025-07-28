"""Tests for async WebSocket streaming."""

import importlib
import json
import os

import pytest

os.environ.setdefault("POLYGON_API_KEY", "test")

from trading_platform.collector import alerts, stream_async


class FakeWS:
    def __init__(self, url, urls):
        self.url = url
        self.urls = urls
        self.urls.append(url)
        if url == stream_async.REALTIME_WS_URL:
            self.messages = [
                json.dumps([{"status": "error", "message": "not authorized"}])
            ]
        else:
            self.messages = [
                json.dumps([{"status": "auth_success"}]),
                json.dumps([{"ev": "T", "sym": "AAPL", "s": 15000}]),
            ]

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
async def test_stream_quotes_reconnect(monkeypatch):
    importlib.reload(stream_async)
    urls = []

    def fake_connect(url):
        return FakeWS(url, urls)

    monkeypatch.setattr(
        stream_async, "websockets", type("W", (), {"connect": fake_connect})
    )

    await stream_async.stream_quotes("AAPL", realtime=True)

    assert urls == [stream_async.REALTIME_WS_URL, stream_async.WS_URL]


@pytest.mark.asyncio
async def test_stream_quotes_alert(monkeypatch):
    importlib.reload(stream_async)
    urls = []

    def fake_connect(url):
        return FakeWS(url, urls)

    monkeypatch.setattr(
        stream_async, "websockets", type("W", (), {"connect": fake_connect})
    )

    agg = alerts.AlertAggregator(webhook_url=None)
    await stream_async.stream_quotes("AAPL", alert_agg=agg, trade_threshold=10000)
    assert any("Large trade" in m for m in agg._messages)
