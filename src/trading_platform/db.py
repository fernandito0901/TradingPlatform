"""Lightweight DB utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path
import csv

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "demo_news.csv"


def bootstrap(path: Path) -> sqlite3.Connection:
    """Ensure required tables exist and return connection."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS news(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at DATETIME
        )"""
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM news")
    if cur.fetchone()[0] == 0 and DATA_FILE.exists():
        with DATA_FILE.open() as f:
            rows = [
                tuple(r[c] for c in ["title", "url", "published_at"])
                for r in csv.DictReader(f)
            ]
        cur.executemany(
            "INSERT INTO news(title, url, published_at) VALUES(?,?,?)",
            rows,
        )
        conn.commit()
    conn.commit()
    return conn
