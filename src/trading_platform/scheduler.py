"""Simple APScheduler wrapper for running the daily pipeline."""

from __future__ import annotations

import time
from apscheduler.schedulers.background import BackgroundScheduler

from .config import load_config, Config
from .run_daily import run as run_daily


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
    return sched


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for the scheduler."""
    cfg = load_config(argv)
    start(cfg)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
