"""Tests for collector API helpers."""

import importlib
import os

# Ensure API keys for module import
os.environ.setdefault("POLYGON_API_KEY", "test")
os.environ.setdefault("NEWS_API_KEY", "test")

from trading_platform.collector import api, db


def fake_rate_get(url, params=None):
    return {"results": [{"t": 1, "o": 1, "h": 1, "l": 1, "c": 1, "v": 10}]}


def test_fetch_ohlcv(monkeypatch):
    importlib.reload(api)
    conn = db.init_db(":memory:")
    monkeypatch.setattr(api, "rate_limited_get", fake_rate_get)
    api.fetch_ohlcv(conn, "AAPL")
    count = conn.execute("SELECT COUNT(*) FROM ohlcv").fetchone()[0]
    assert count == 1


def test_fetch_minute_bars(monkeypatch):
    importlib.reload(api)
    conn = db.init_db(":memory:")
    monkeypatch.setattr(api, "rate_limited_get", fake_rate_get)
    api.fetch_minute_bars(conn, "AAPL")
    count = conn.execute("SELECT COUNT(*) FROM minute_bars").fetchone()[0]
    assert count == 1


def test_http_cache(monkeypatch):
    monkeypatch.setenv("CACHE_TTL", "10")
    importlib.reload(api)

    calls = []

    def fake_get(url, params=None):
        calls.append(1)

        class Resp:
            status_code = 200

            def json(self):
                return {"ok": True}

            def raise_for_status(self):
                pass

        return Resp()

    monkeypatch.setattr(api, "RATE_LIMIT_SEC", 0)
    monkeypatch.setattr(api.requests, "get", fake_get)

    api.rate_limited_get("https://example.com", {"q": "a"})
    api.rate_limited_get("https://example.com", {"q": "a"})

    assert len(calls) == 1


def test_fetch_news(monkeypatch):
    importlib.reload(api)
    conn = db.init_db(":memory:")

    def fake_news(url, params=None):
        return {
            "articles": [
                {
                    "publishedAt": "2025-07-30T00:00:00Z",
                    "title": "Foo rises",
                    "url": "https://example.com/foo",
                    "source": {"name": "Example"},
                }
            ]
        }

    monkeypatch.setattr(api, "rate_limited_get", fake_news)
    api.fetch_news(conn, "AAPL")
    count = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    assert count == 1
