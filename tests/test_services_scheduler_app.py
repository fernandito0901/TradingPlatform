import importlib
import importlib.util
from pathlib import Path


def _load_app_module():
    spec = importlib.util.spec_from_file_location(
        "scheduler_app", Path("services/scheduler/app.py")
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_import_without_env(monkeypatch):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    _load_app_module()


def test_main_starts_scheduler(monkeypatch):
    monkeypatch.setenv("POLYGON_API_KEY", "x")
    monkeypatch.setenv("SCHED_INTERVAL", "1")
    started = {}

    def fake_start(cfg, interval=86400, testing=False):
        started["interval"] = interval

        class Dummy:
            def shutdown(self):
                pass

        return Dummy()

    mod = _load_app_module()
    monkeypatch.setattr(mod, "start", fake_start)
    monkeypatch.setattr(mod.health_app, "run", lambda **k: None)

    def sleep(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(mod.time, "sleep", sleep)

    mod.main()
    assert started["interval"] == 1
