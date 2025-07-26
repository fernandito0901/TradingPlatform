"""Simple APScheduler wrapper for running the daily pipeline."""

from __future__ import annotations

import time
import os
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv

socketio: SocketIO | None = None

from .config import load_config, Config
from .run_daily import run as run_daily

health_app = Flask(__name__)


@health_app.route("/healthz")
def healthz():
    return jsonify(status="ok")


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
    sched.start()

    global socketio
    socketio = SocketIO(message_queue=os.getenv("REDIS_URL"))

    if socketio.server:
        sched.add_job(lambda: socketio.emit("scheduler-alive"), "interval", seconds=60)
        socketio.emit("scheduler-alive")
    else:
        import logging

        logging.getLogger(__name__).warning("Socket.IO not available, skipping emit")
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
