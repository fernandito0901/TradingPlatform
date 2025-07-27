"""Tests for historical backfill utility."""

import importlib
from datetime import datetime

from trading_platform.collector import api, backfill, db


def test_fetch_range_inserts(monkeypatch):
    importlib.reload(backfill)
    conn = db.init_db(":memory:")
    ts_existing = int(datetime(2025, 1, 1).timestamp() * 1000)
    conn.execute(
        "INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)",
        ("AAPL", ts_existing, 1, 1, 1, 1, 10),
    )

    ts_new = int(datetime(2025, 1, 2).timestamp() * 1000)

    def fake_get(url, params=None):
        return {"results": [{"t": ts_new, "o": 1, "h": 1, "l": 1, "c": 1, "v": 20}]}

    monkeypatch.setattr(api, "rate_limited_get", fake_get)

    count = backfill.fetch_range(conn, "AAPL", "2025-01-02", "2025-01-02")
    assert count == 1
    assert conn.execute("SELECT COUNT(*) FROM ohlcv").fetchone()[0] == 2
