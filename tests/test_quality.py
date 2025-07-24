"""Tests for data quality report."""

import importlib
from datetime import datetime

from trading_platform.collector import quality, db


def test_quality_report(monkeypatch):
    importlib.reload(quality)
    conn = db.init_db(":memory:")
    ts1 = int(datetime(2025, 1, 1).timestamp() * 1000)
    ts3 = int(datetime(2025, 1, 3).timestamp() * 1000)
    conn.execute(
        "INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)",
        ("AAPL", ts1, 1, 1, 1, 1, 10),
    )
    conn.execute(
        "INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)",
        ("AAPL", ts3, 1, 1, 1, 1, 10),
    )
    conn.execute(
        "INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)",
        ("MSFT", ts1, None, 1, 1, 1, 10),
    )
    conn.commit()

    report = quality.quality_report(conn)
    rep = {r["symbol"]: r for r in report}
    assert rep["AAPL"]["missing_days"] == 1
    assert rep["AAPL"]["nulls"] == 0
    assert rep["MSFT"]["missing_days"] == 0
    assert rep["MSFT"]["nulls"] == 1
