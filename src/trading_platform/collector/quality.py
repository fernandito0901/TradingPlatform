import argparse
import pandas as pd

from ..load_env import load_env
from . import db


def quality_report(conn) -> list[dict]:
    """Return quality metrics for each symbol in ``ohlcv``.

    Parameters
    ----------
    conn : sqlite3.Connection
        Database connection containing OHLCV data.

    Returns
    -------
    list of dict
        Each dict contains ``symbol``, ``missing_days`` and ``nulls`` keys.
    """
    symbols = [r[0] for r in conn.execute("SELECT DISTINCT symbol FROM ohlcv")]
    reports = []
    for sym in symbols:
        df = pd.read_sql_query(
            "SELECT t, open, high, low, close, volume FROM ohlcv WHERE symbol=?",
            conn,
            params=(sym,),
        )
        if df.empty:
            continue
        df["date"] = pd.to_datetime(df["t"], unit="ms").dt.date
        expected = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
        missing = len(set(expected.date) - set(df["date"]))
        nulls = int(df.isna().sum().sum())
        reports.append({"symbol": sym, "missing_days": missing, "nulls": nulls})
    return reports


def main(argv: list[str] | None = None) -> int:
    """CLI entry point printing quality metrics."""
    load_env()
    parser = argparse.ArgumentParser(description="Data quality report")
    parser.add_argument("--db-file", default="market_data.db")
    args = parser.parse_args(argv)
    conn = db.init_db(args.db_file)
    for item in quality_report(conn):
        print(
            f"{item['symbol']}: missing {item['missing_days']} days, {item['nulls']} nulls"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
