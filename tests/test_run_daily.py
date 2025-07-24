"""Tests for daily pipeline orchestration."""

import importlib
import pytest

from trading_platform import run_daily


def test_run_daily_abort(monkeypatch):
    importlib.reload(run_daily)

    monkeypatch.setattr(run_daily.verify, "verify", lambda symbols: False)
    with pytest.raises(SystemExit):
        run_daily.run("AAPL")


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

    def fake_generate(csv, model_file, out_dir="playbooks"):
        path = tmp_path / "pb.json"
        path.write_text("{}")
        return str(path)

    monkeypatch.setattr(run_daily, "generate_playbook", fake_generate)

    res = run_daily.run("AAPL", db_file=str(tmp_path / "db.sqlite"))
    assert res.endswith("pb.json")
    assert called["fetch"] == ["AAPL"]
