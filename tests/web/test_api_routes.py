import os
import sqlite3
from pathlib import Path

from trading_platform.webapp import create_app


def test_metrics_empty_when_auc_missing(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    app = create_app(env_path=env)
    csv = Path(os.environ["REPORTS_DIR"]) / "pnl.csv"
    csv.unlink(missing_ok=True)
    csv.write_text("total\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json.get("status") == "empty"


def test_overview_empty(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    monkeypatch.setattr(
        "trading_platform.collector.api.fetch_prev_close",
        lambda s: {"results": [{"c": 100}]},
    )
    app = create_app(env_path=env)
    conn = sqlite3.connect("market_data.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS ohlcv (symbol TEXT, t INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL)"
    )
    conn.close()
    client = app.test_client()
    resp = client.get("/api/overview")
    assert resp.json == {"status": "empty"}
