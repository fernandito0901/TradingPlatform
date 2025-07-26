from pathlib import Path
from trading_platform.webapp import create_app


def test_api_metrics_handles_empty_row(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "scoreboard.csv"
    csv.write_text("date,train_auc,test_auc,cv_auc,auc\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}


def test_api_metrics_nan_row(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "scoreboard.csv"
    csv.write_text("date,train_auc,test_auc,cv_auc,auc\n2025-01-01,,,,\n")
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}


def test_api_metrics_missing_file(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    client = app.test_client()
    resp = client.get("/api/metrics")
    assert resp.json == {"status": "empty"}


def test_api_performance_metrics(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    csv = reports / "pnl.csv"
    csv.write_text("total\n100\n110\n120\n")
    client = app.test_client()
    resp = client.get("/api/metrics/performance")
    assert set(resp.json.keys()) == {"sharpe", "sortino"}
