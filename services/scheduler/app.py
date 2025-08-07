import logging
import os
import time
from threading import Thread

from trading_platform.load_env import load_env
from trading_platform.config import load_config
from trading_platform.scheduler import start, health_app


log = logging.getLogger(__name__)


def main() -> None:
    """Entry point for the scheduler service."""
    load_env()
    try:
        cfg = load_config()
    except Exception as exc:  # pragma: no cover - config errors
        log.error("Failed to load config: %s", exc)
        return

    interval = os.getenv("SCHED_INTERVAL")
    health_port = int(os.getenv("HEALTH_PORT", "8001"))
    try:
        if interval:
            sched = start(cfg, interval=int(interval), testing=True)
        else:
            sched = start(cfg)
    except Exception as exc:  # pragma: no cover - startup issues
        log.error("Scheduler failed: %s", exc)
        return

    Thread(
        target=health_app.run, kwargs={"host": "0.0.0.0", "port": health_port}
    ).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        sched.shutdown()


if __name__ == "__main__":
    main()
