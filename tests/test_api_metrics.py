from pathlib import Path
from trading_platform.webapp import create_app


def test_api_metrics_empty(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}


def test_api_metrics_values(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "pnl.csv"
    csv.write_text("date,total\n2025-01-01,1\n2025-01-02,2\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json["status"] == "ok"


def test_api_metrics_missing_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}
