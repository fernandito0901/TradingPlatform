"""Tests for Flask web interface."""

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

    monkeypatch.setattr("trading_platform.webapp.scheduler_mod.start", fake_start)

    client.post("/start_scheduler")
    assert started
    resp = client.get("/")
    assert b"Stop Scheduler" in resp.data

    client.post("/stop_scheduler")
    resp = client.get("/")
    assert b"Start Scheduler" in resp.data
