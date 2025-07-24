"""Tests for feature engineering pipeline."""

import sqlite3

from trading_platform.features import pipeline


def test_compute_features_from_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE ohlcv (symbol TEXT, t INTEGER, close REAL, open REAL, high REAL, low REAL, volume REAL, PRIMARY KEY(symbol, t))"
    )
    rows = [("AAPL", i, float(i), 0, 0, 0, 0) for i in range(1, 61)]
    conn.executemany("INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)", rows)

    conn.execute(
        "CREATE TABLE option_chain (symbol TEXT, contract TEXT, expiration DATE, strike REAL, option_type TEXT, bid REAL, ask REAL, iv REAL, delta REAL, volume REAL, open_interest REAL, PRIMARY KEY(symbol, contract))"
    )
    conn.execute(
        "INSERT INTO option_chain VALUES ('AAPL','AAPL2301','2025-08-30',100,'c',1,1,0.3,0.5,10,100)"
    )

    conn.execute(
        "CREATE TABLE news (symbol TEXT, published_at TEXT, title TEXT, url TEXT, source TEXT, PRIMARY KEY(symbol, published_at, title))"
    )
    conn.execute(
        "INSERT INTO news VALUES ('AAPL','2025-07-31','Apple shares rise on strong demand','https://example.com','Example')"
    )

    df = pipeline.from_db(conn, "AAPL")
    assert "sma20" in df.columns
    assert "rsi14" in df.columns
    assert "hv30" in df.columns
    assert "iv30" in df.columns
    assert "garch_sigma" in df.columns
    assert "news_sent" in df.columns
    assert "uoa" in df.columns
    assert "iv_edge" in df.columns
    assert "garch_spike" in df.columns
    assert len(df) > 0
