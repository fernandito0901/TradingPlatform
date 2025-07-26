from pathlib import Path
import sqlite3
from trading_platform.webapp import create_app


def test_metrics_empty_when_auc_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    app = create_app(env_path=env)
    csv = Path(app.static_folder) / "scoreboard.csv"
    csv.write_text("date,auc\n2025-01-01,\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}


def test_overview_empty(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    monkeypatch.setattr(
        "trading_platform.collector.api.fetch_snapshot_tickers",
        lambda: {"tickers": []},
    )
    app = create_app(env_path=env)
    conn = sqlite3.connect("market_data.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ohlcv (symbol TEXT, t INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL)"
    )
    conn.close()
    client = app.test_client()
    resp = client.get("/api/overview")
    assert resp.json == []
