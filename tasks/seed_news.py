"""Seed the news table with sample rows if empty."""

from trading_platform.collector import db
from trading_platform.reports import REPORTS_DIR
from pathlib import Path
import csv

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "demo_news.csv"


def main() -> None:
    path = REPORTS_DIR / "scoreboard.db"
    conn = db.init_db(str(path))
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
    conn.close()


if __name__ == "__main__":
    main()
