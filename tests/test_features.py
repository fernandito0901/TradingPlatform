"""Tests for feature engineering pipeline."""

import sqlite3

from trading_platform.features import pipeline


def test_compute_features_from_db(monkeypatch):
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

    monkeypatch.setattr(
        pipeline,
        "fetch_open_close",
        lambda s, d: {"open": 1, "high": 1, "low": 1, "previousClose": 1},
    )
    monkeypatch.setattr(pipeline, "fetch_prev_close", lambda s: {"results": [{"c": 1}]})
    monkeypatch.setattr(
        pipeline, "fetch_trades", lambda s: {"results": [{"p": 1, "s": 1}]}
    )
    monkeypatch.setattr(
        pipeline, "fetch_quotes", lambda s: {"results": [{"bp": 1, "ap": 1}]}
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


def test_pipeline_adds_intraday_features(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE ohlcv (symbol TEXT, t INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL, PRIMARY KEY(symbol, t))"
    )
    rows = [("AAPL", i, 1.0, 2.0, 0.5, float(i), 100.0) for i in range(1, 61)]
    conn.executemany("INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)", rows)
    conn.execute(
        "CREATE TABLE option_chain (symbol TEXT, contract TEXT, expiration DATE, strike REAL, option_type TEXT, bid REAL, ask REAL, iv REAL, delta REAL, volume REAL, open_interest REAL, PRIMARY KEY(symbol, contract))"
    )
    conn.execute(
        "INSERT INTO option_chain VALUES ('AAPL','C','2025-12-31',100,'c',1,1,0.3,0.5,10,100)"
    )
    conn.execute(
        "CREATE TABLE news (symbol TEXT, published_at TEXT, title TEXT, url TEXT, source TEXT, PRIMARY KEY(symbol, published_at, title))"
    )
    conn.execute(
        "INSERT INTO news VALUES ('AAPL','2025-07-31','Foo up','https://ex.com','Ex')"
    )

    monkeypatch.setattr(
        pipeline,
        "fetch_open_close",
        lambda s, d: {"open": 10, "high": 12, "low": 8, "previousClose": 9},
    )
    monkeypatch.setattr(pipeline, "fetch_prev_close", lambda s: {"results": [{"c": 9}]})
    monkeypatch.setattr(
        pipeline,
        "fetch_trades",
        lambda s: {"results": [{"p": 10, "s": 1}, {"p": 11, "s": 1}]},
    )
    monkeypatch.setattr(
        pipeline, "fetch_quotes", lambda s: {"results": [{"bp": 9, "ap": 10}]}
    )

    df = pipeline.from_db(conn, "AAPL")
    for col in ["gap_up", "gap_down", "intraday_atr", "spread", "vwap"]:
        assert col in df.columns
