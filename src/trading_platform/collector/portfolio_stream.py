from __future__ import annotations

"""Stream quotes for portfolio symbols and log them to the database."""

import argparse
import asyncio
import logging
from pathlib import Path
import sqlite3

import pandas as pd

from ..portfolio import PORTFOLIO_FILE
from . import db, stream_async


def portfolio_symbols(portfolio_file: str = PORTFOLIO_FILE) -> list[str]:
    """Return unique symbols from the portfolio file."""
    file = Path(portfolio_file)
    if not file.exists():
        return []
    df = pd.read_csv(file)
    if df.empty or "symbol" not in df.columns:
        return []
    return sorted(df["symbol"].unique().tolist())


async def _save_event(conn: sqlite3.Connection, event: dict) -> None:
    """Persist a trade or quote event into ``realtime_quotes``."""
    if event.get("ev") not in {"T", "Q"}:
        return
    sym = event.get("sym") or event.get("symbol")
    price = event.get("p") or event.get("bp") or event.get("ap")
    ts = event.get("t") or event.get("timestamp")
    if sym and price and ts:
        conn.execute(
            "INSERT OR REPLACE INTO realtime_quotes VALUES (?,?,?)", (sym, ts, price)
        )
        conn.commit()


async def stream_portfolio_quotes(
    conn: sqlite3.Connection,
    portfolio_file: str = PORTFOLIO_FILE,
    realtime: bool = False,
) -> None:
    """Stream WebSocket quotes for all open positions."""
    symbols = portfolio_symbols(portfolio_file)
    if not symbols:
        logging.info("No open positions to stream")
        return

    async def handle(evt: dict) -> None:
        await _save_event(conn, evt)

    await stream_async.stream_quotes(
        ",".join(symbols), realtime=realtime, on_event=handle
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for streaming portfolio quotes."""
    parser = argparse.ArgumentParser(description="Stream portfolio quotes")
    parser.add_argument("--portfolio-file", default=PORTFOLIO_FILE)
    parser.add_argument("--db-file", default="market_data.db")
    parser.add_argument("--realtime", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)
    logging.basicConfig(level=args.log_level)
    conn = db.init_db(args.db_file)
    asyncio.run(
        stream_portfolio_quotes(conn, args.portfolio_file, realtime=args.realtime)
    )


if __name__ == "__main__":
    main()
