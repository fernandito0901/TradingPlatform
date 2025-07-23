"""Logging utilities for the collector package."""

import logging
from typing import Optional


def setup_logging(log_file: Optional[str] = None, level: str = "INFO") -> None:
    """Configure logging to console or file."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        filename=log_file,
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
