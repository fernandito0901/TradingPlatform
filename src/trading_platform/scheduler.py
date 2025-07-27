"""Simple APScheduler wrapper for running the daily pipeline."""

from __future__ import annotations

import time
import os
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from flask_socketio import SocketIO
import logging
from dotenv import load_dotenv

socketio: SocketIO | None = None
_log = logging.getLogger(__name__)

from .config import load_config, Config
from .run_daily import run as run_daily

health_app = Flask(__name__)


@health_app.route("/healthz")
def healthz():
    return jsonify(status="ok")


def _connect_socketio() -> None:
    """Initialise Socket.IO with retries."""
    global socketio
    delay = 1
    while True:
        try:
            socketio = SocketIO(message_queue=os.getenv("REDIS_URL"))
            if socketio.server:
                _log.info("Socket.IO connected")
                break
        except Exception as exc:  # pragma: no cover - network errors
            _log.warning("Socket.IO connection failed: %s", exc)
        time.sleep(delay)
        delay = min(delay * 2, 60)


def _emit_alive() -> None:
    if socketio and socketio.server:
        try:
            socketio.emit("scheduler-alive")
        except Exception as exc:  # pragma: no cover
            _log.warning("Emit failed: %s", exc)
    else:
        _log.warning("Socket.IO not available, skipping emit")


def _log_heartbeat() -> None:
    _log.info("scheduler_heartbeat - alive")


def start(
    config: Config, interval: int = 86400, run_func=run_daily
) -> BackgroundScheduler:
    """Start a background scheduler for ``run_daily``.

    Parameters
    ----------
    config : Config
        Runtime configuration.
    interval : int, optional
        Interval between runs in seconds, by default 86400 (once per day).
    run_func : callable, optional
        Function executed on schedule, by default :func:`run_daily`.

    Returns
    -------
    BackgroundScheduler
        The started scheduler instance.
    """
    sched = BackgroundScheduler()
    sched.add_job(run_func, "interval", seconds=interval, args=(config,))
    sched.add_job(_log_heartbeat, "interval", seconds=30)
    sched.start()

    Thread(target=_connect_socketio, daemon=True).start()
    sched.add_job(_emit_alive, "interval", seconds=60)
    return sched


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for the scheduler."""
    load_dotenv()
    cfg = load_config(argv)
    start(cfg)
    Thread(target=health_app.run, kwargs={"host": "0.0.0.0", "port": 8001}).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
