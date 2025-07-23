import sqlite3
import pandas as pd
from features import pipeline


def test_compute_features_from_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE ohlcv (symbol TEXT, t INTEGER, close REAL, open REAL, high REAL, low REAL, volume REAL, PRIMARY KEY(symbol, t))"
    )
    rows = [("AAPL", i, float(i), 0, 0, 0, 0) for i in range(1, 61)]
    conn.executemany("INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)", rows)

    df = pipeline.from_db(conn, "AAPL")
    assert "sma20" in df.columns
    assert "rsi14" in df.columns
    assert len(df) > 0
