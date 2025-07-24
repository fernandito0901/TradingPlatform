"""Tests for async collector API."""

import importlib
import os

import pytest

os.environ.setdefault("POLYGON_API_KEY", "test")
os.environ.setdefault("NEWS_API_KEY", "test")

from trading_platform.collector import api_async, db


class FakeResp:
    def __init__(self, data):
        self.data = data
        self.status = 200
        self.request_info = None
        self.history = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def json(self):
        return self.data

    def raise_for_status(self):
        pass


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def get(self, url, params=None):
        return FakeResp({"results": []})


@pytest.mark.asyncio
async def test_fetch_all(monkeypatch):
    importlib.reload(api_async)
    conn = db.init_db(":memory:")
    session = FakeSession()

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return session

        async def __aexit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr(
        api_async, "aiohttp", type("A", (), {"ClientSession": FakeClient})
    )

    await api_async.fetch_all(conn, "AAPL")
