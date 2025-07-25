from trading_platform.scheduler import start
from trading_platform.config import Config
import time


def test_scheduler_runs(monkeypatch):
    calls = []

    def fake_run(cfg):
        calls.append(cfg.symbols)

    cfg = Config(symbols="AAPL")
    sched = start(cfg, interval=0.1, run_func=fake_run)
    time.sleep(0.25)
    sched.shutdown()
    assert calls
