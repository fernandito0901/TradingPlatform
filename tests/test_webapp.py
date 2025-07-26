"""Tests for Flask web interface."""

from pathlib import Path
import os
from trading_platform.webapp import create_app


def test_setup_creates_env(tmp_path, monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    env = tmp_path / ".env"
    app = create_app(env_path=env)
    client = app.test_client()

    resp = client.get("/")
    assert b"Setup" in resp.data

    client.post("/", data={"polygon_api_key": "abc"})
    assert env.exists()
    assert "POLYGON_API_KEY=abc" in env.read_text()

    resp = client.get("/")
    assert b"Run Daily Pipeline" in resp.data


def test_scheduler_controls(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    app = create_app(env_path=env)
    client = app.test_client()

    started = False

    def fake_start(cfg, interval=86400, run_func=None):
        nonlocal started
        started = True

        class Dummy:
            def shutdown(self):
                pass

        return Dummy()

    monkeypatch.setattr("trading_platform.scheduler.start", fake_start)

    client.post("/start_scheduler")
    assert started
    resp = client.get("/")
    assert b"Stop Scheduler" in resp.data

    client.post("/stop_scheduler")
    resp = client.get("/")
    assert b"Start Scheduler" in resp.data


def test_scoreboard_with_risk_columns(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    csv = tmp_path / "scoreboard.csv"
    csv.write_text(
        "date,playbook,auc,pnl\n2025-01-01,p1,0.7,1\n2025-01-02,p2,0.8,-0.5\n"
    )
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    client = app.test_client()
    resp = client.get("/")
    assert b"sharpe" in resp.data
    assert b"max_drawdown" in resp.data


def test_api_watchlist_and_alerts(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\nSYMBOLS=AAPL,MSFT\n")
    log = tmp_path / "alerts.log"
    log.write_text("Alert one\nAlert two\n")
    monkeypatch.setattr("trading_platform.collector.alerts.ALERT_LOG", str(log))
    app = create_app(env_path=env)
    client = app.test_client()

    resp = client.get("/api/watchlist")
    assert resp.json == ["AAPL", "MSFT"]

    resp = client.get("/api/alerts")
    assert resp.json[-1] == "Alert two"


def test_api_scoreboard_and_pnl(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    app = create_app(env_path=env)
    csv = Path(app.static_folder) / "scoreboard.csv"
    pnl = Path("reports/pnl.csv")
    pnl.parent.mkdir(parents=True, exist_ok=True)
    csv.write_text("date,playbook,auc\n2025-01-01,p1,0.7\n")
    pnl.write_text("date,symbol,unrealized,realized,total\n2025-01-01,A,0,0,0\n")
    client = app.test_client()

    resp = client.get("/api/scoreboard")
    assert resp.json[0]["auc"] == 0.7

    resp = client.get("/api/pnl")
    assert resp.json[0]["symbol"] == "A"


def test_api_latest_features_and_options(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=abc\n")
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    feat_csv = features_dir / "2025-01-01.csv"
    feat_csv.write_text("t,close,target\n1,1,0\n")
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    meta = models_dir / "model_1_metadata.json"
    meta.write_text('{"train_auc": 0.9}')
    options_csv = tmp_path / "options_chain.2025-01-01.csv"
    options_csv.write_text("strike,price,iv\n100,1,0.5\n")

    cwd = os.getcwd()
    os.chdir(tmp_path)
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    client = app.test_client()
    resp = client.get("/api/features/latest")
    assert resp.json["features"].endswith("2025-01-01.csv")
    os.chdir(cwd)

    resp = client.get("/api/options/2025-01-01")
    assert resp.json[0]["strike"] == 100
