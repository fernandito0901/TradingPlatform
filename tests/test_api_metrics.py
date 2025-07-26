from pathlib import Path
from trading_platform.webapp import create_app


def test_api_metrics_handles_empty_row(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "pnl.csv"
    csv.write_text("total\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"total_return": 0.0, "pnl": 0.0}


def test_api_metrics_nan_row(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "pnl.csv"
    csv.write_text("total\n1\n\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"total_return": 0.0, "pnl": 1.0}


def test_api_metrics_missing_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"total_return": 0.0, "pnl": 0.0}


def test_api_performance_metrics(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "pnl.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    csv.write_text("total\n100\n110\n120\n")
    client = app.test_client()
    resp = client.get("/api/metrics/performance")
    assert set(resp.json.keys()) == {"sharpe", "sortino"}
