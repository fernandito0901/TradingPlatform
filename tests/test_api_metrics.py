import os
from pathlib import Path

from trading_platform.webapp import create_app


def test_api_metrics_empty(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    csv = Path(os.environ["REPORTS_DIR"]) / "pnl.csv"
    if csv.exists():
        csv.unlink()
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json.get("status") == "empty"


def test_api_metrics_values(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    csv = Path(os.environ["REPORTS_DIR"]) / "pnl.csv"
    csv.write_text("pnl\n1\n2\n-1\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 3


def test_api_metrics_missing_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    csv = Path(os.environ["REPORTS_DIR"]) / "pnl.csv"
    if csv.exists():
        csv.unlink()
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}
