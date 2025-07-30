import argparse
import datetime as _dt

from ..load_env import load_env
from . import api, db


def fetch_range(conn, symbol: str, start: str, end: str) -> int:
    """Download missing OHLCV rows for the given date range.

    Parameters
    ----------
    conn : sqlite3.Connection
        Database connection with an ``ohlcv`` table.
    symbol : str
        Ticker symbol to backfill.
    start : str
        Start date ``YYYY-MM-DD``.
    end : str
        End date ``YYYY-MM-DD``.

    Returns
    -------
    int
        Number of bars inserted into the database.
    """
    s = _dt.date.fromisoformat(start)
    e = _dt.date.fromisoformat(end)
    if s > e:
        raise ValueError("start date after end date")

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{s}/{e}"
    params = {"adjusted": "true", "apiKey": api._get_polygon_key()}
    data = api.rate_limited_get(url, params)
    inserted = 0
    c = conn.cursor()
    for bar in data.get("results", []):
        ts = bar["t"]
        cur = c.execute(
            "SELECT 1 FROM ohlcv WHERE symbol=? AND t=?", (symbol, ts)
        ).fetchone()
        if cur:
            continue
        c.execute(
            "INSERT OR REPLACE INTO ohlcv VALUES (?,?,?,?,?,?,?)",
            (
                symbol,
                ts,
                bar["o"],
                bar["h"],
                bar["l"],
                bar["c"],
                bar["v"],
            ),
        )
        inserted += 1
    conn.commit()
    return inserted


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for backfilling missing bars."""
    load_env()
    parser = argparse.ArgumentParser(description="Backfill historical OHLCV")
    parser.add_argument("symbol", help="Ticker symbol")
    parser.add_argument("start", help="Start date YYYY-MM-DD")
    parser.add_argument("end", help="End date YYYY-MM-DD")
    parser.add_argument("--db-file", default="market_data.db")
    args = parser.parse_args(argv)

    conn = db.init_db(args.db_file)
    count = fetch_range(conn, args.symbol, args.start, args.end)
    print(f"Inserted {count} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
