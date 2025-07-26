"""Seed the news table with sample rows if empty."""

from trading_platform.collector import db
from trading_platform.reports import REPORTS_DIR

SAMPLE = [
    ("AAPL", "Apple launches new product", "https://example.com/a", "2025-01-01"),
    ("GOOG", "Google earnings beat", "https://example.com/g", "2025-01-02"),
    ("MSFT", "Microsoft announces merger", "https://example.com/m", "2025-01-03"),
]


def main() -> None:
    path = REPORTS_DIR / "scoreboard.db"
    conn = db.init_db(str(path))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM news")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO news(symbol, title, url, published_at) VALUES(?,?,?,?)",
            SAMPLE,
        )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
