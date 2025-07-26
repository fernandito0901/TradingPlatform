"""Lightweight DB utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def bootstrap(path: Path) -> sqlite3.Connection:
    """Ensure required tables exist and return connection."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS news(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    return conn
