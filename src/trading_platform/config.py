from __future__ import annotations

"""Unified configuration dataclass and loader."""

import argparse
import os
from dataclasses import dataclass

from .load_env import load_env


def _parse_risk(value: str | None) -> dict[str, float] | None:
    """Parse a comma-separated risk string into a dictionary."""
    if not value:
        return None
    result: dict[str, float] = {}
    for pair in value.split(","):
        if "=" not in pair:
            continue
        name, val = pair.split("=", 1)
        try:
            result[name.strip()] = float(val)
        except ValueError:
            continue
    return result


@dataclass
class Config:
    """Runtime configuration options."""

    symbols: str = "AAPL"
    db_file: str = "market_data.db"
    use_async: bool = False
    log_file: str | None = None
    log_level: str = "INFO"
    polygon_api_key: str | None = None
    news_api_key: str | None = None
    slack_webhook_url: str | None = None
    max_risk: dict[str, float] | None = None


def load_config(
    argv: list[str] | None = None, env_path: str | os.PathLike[str] = ".env"
) -> Config:
    """Load configuration from a ``.env`` file and command-line arguments."""

    load_env(env_path)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--symbols", default=os.getenv("SYMBOLS", "AAPL"))
    parser.add_argument("--db-file", default=os.getenv("DB_FILE", "market_data.db"))
    parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        default=os.getenv("USE_ASYNC") == "1",
    )
    parser.add_argument("--log-file", default=os.getenv("LOG_FILE"))
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    parser.add_argument("--max-risk", default=os.getenv("MAX_RISK"))
    args, _ = parser.parse_known_args(argv)

    return Config(
        symbols=args.symbols,
        db_file=args.db_file,
        use_async=args.use_async,
        log_file=args.log_file,
        log_level=args.log_level,
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
        news_api_key=os.getenv("NEWS_API_KEY"),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
        max_risk=_parse_risk(args.max_risk),
    )
