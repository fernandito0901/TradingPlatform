"""Tests for daily pipeline orchestration."""

import importlib
import pytest

load_env_module = importlib.import_module("trading_platform.load_env")

from trading_platform import run_daily
from trading_platform.config import Config


def test_run_daily_abort(monkeypatch):
    importlib.reload(run_daily)

    monkeypatch.setattr(run_daily.verify, "verify", lambda symbols: False)
    cfg = Config(symbols="AAPL")
    with pytest.raises(SystemExit):
        run_daily.run(cfg)


def test_run_daily_notify_failure(monkeypatch, tmp_path):
    importlib.reload(run_daily)

    monkeypatch.setattr(run_daily.verify, "verify", lambda symbols: True)

    def fake_fetch_ohlcv(conn, sym):
        pass

    monkeypatch.setattr(run_daily.api, "fetch_ohlcv", fake_fetch_ohlcv)
    monkeypatch.setattr(run_daily.api, "fetch_option_chain", lambda *a: None)
    monkeypatch.setattr(run_daily.api, "fetch_news", lambda *a: None)

    monkeypatch.setattr(run_daily, "run_pipeline", lambda *a, **k: "features.csv")

    def fail_train(csv, model_path="models/model.txt"):
        raise RuntimeError("boom")

    monkeypatch.setattr(run_daily, "train_model", fail_train)

    sent = []

    def fake_slack(msg, webhook_url=None):
        sent.append(msg)

    monkeypatch.setattr(run_daily.notifier, "send_slack", fake_slack)

    cfg = Config(symbols="AAPL", db_file=str(tmp_path / "db.sqlite"))
    with pytest.raises(RuntimeError):
        run_daily.run(cfg)

    assert sent and "failed" in sent[0]


def test_run_daily_success(monkeypatch, tmp_path):
    importlib.reload(run_daily)

    monkeypatch.setattr(run_daily.verify, "verify", lambda symbols: True)

    called = {}

    def fake_fetch_ohlcv(conn, sym):
        called.setdefault("fetch", []).append(sym)

    def fake_fetch_option_chain(conn, sym):
        pass

    def fake_fetch_news(conn, sym):
        pass

    monkeypatch.setattr(run_daily.api, "fetch_ohlcv", fake_fetch_ohlcv)
    monkeypatch.setattr(run_daily.api, "fetch_option_chain", fake_fetch_option_chain)
    monkeypatch.setattr(run_daily.api, "fetch_news", fake_fetch_news)

    def fake_run_pipeline(conn, sym, out_dir="features"):
        path = tmp_path / "feat.csv"
        path.write_text("t,close\n1,1")
        return str(path)

    monkeypatch.setattr(run_daily, "run_pipeline", fake_run_pipeline)

    def fake_train(csv, model_path="models/model.txt"):
        return 0.5, 0.5

    monkeypatch.setattr(run_daily, "train_model", fake_train)

    monkeypatch.setattr(run_daily, "generate_dashboard", lambda *a, **k: "dash.html")
    monkeypatch.setattr(run_daily, "update_scoreboard", lambda *a, **k: "sb.csv")

    def fake_generate(csv, model_file, out_dir="playbooks"):
        path = tmp_path / "pb.json"
        path.write_text("{}")
        return str(path)

    monkeypatch.setattr(run_daily, "generate_playbook", fake_generate)

    sent = []

    def fake_slack(msg, webhook_url=None):
        sent.append(msg)

    monkeypatch.setattr(run_daily.notifier, "send_slack", fake_slack)

    cfg = Config(symbols="AAPL", db_file=str(tmp_path / "db.sqlite"))
    res = run_daily.run(cfg)
    assert res.endswith("pb.json")
    assert called["fetch"] == ["AAPL"]
    assert sent == [f"Pipeline completed: {res}"]
