import time

from trading_platform.config import Config
from trading_platform.scheduler import start


def test_scheduler_runs(monkeypatch):
    calls = []

    def fake_run(cfg):
        calls.append(cfg.symbols)

    cfg = Config(symbols="AAPL")
    sched = start(cfg, interval=0.1, run_func=fake_run)
    time.sleep(0.25)
    sched.shutdown()
    assert calls


def test_scheduler_socketio_retry(monkeypatch):
    from trading_platform import scheduler as sched_mod

    class BadSocket:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("connect failed")

    monkeypatch.setattr(sched_mod, "SocketIO", BadSocket)
    cfg = Config(symbols="AAPL")
    sched = sched_mod.start(cfg, interval=1, run_func=lambda c: None)
    time.sleep(5)
    assert sched.running
    sched.shutdown()
