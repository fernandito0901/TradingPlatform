import sqlite3
from trading_platform.webapp import create_app


def test_overview_snapshot(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")

    def fake_prev(symbol: str):
        return {"results": [{"c": 100}]}

    monkeypatch.setattr("trading_platform.collector.api.fetch_prev_close", fake_prev)

    app = create_app(env_path=env)
    client = app.test_client()

    resp = client.get("/api/overview")
    assert resp.json == {"status": "empty"}


def test_overview_empty_when_nan(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    app = create_app(env_path=env)
    conn = sqlite3.connect("market_data.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ohlcv (symbol TEXT, t INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL)"
    )
    conn.execute(
        "INSERT INTO ohlcv VALUES (?,?,?,?,?,?,?)",
        ("AAPL", 0, 0, 0, 0, None, 0),
    )
    conn.commit()
    conn.close()
    client = app.test_client()
    resp = client.get("/api/overview")
    assert resp.json == {"status": "empty"}


def test_overview_empty_csv(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    app = create_app(env_path=env)
    client = app.test_client()
    resp = client.get("/api/overview")
    assert resp.json == {"status": "empty"}
