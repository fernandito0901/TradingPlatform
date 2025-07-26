"""Exit simulation utilities updating PnL."""

from __future__ import annotations

from datetime import datetime
import sqlite3

import pandas as pd

from trading_platform import portfolio


def update_unrealized_pnl(
    conn: sqlite3.Connection,
    portfolio_file: str = portfolio.PORTFOLIO_FILE,
    pnl_file: str = portfolio.PNL_FILE,
) -> str:
    """Update PnL CSV with unrealized PnL based on latest quotes.

    Parameters
    ----------
    conn : sqlite3.Connection
        Database connection containing the ``realtime_quotes`` table.
    portfolio_file : str, optional
        Path to ``portfolio.csv`` with open positions.
    pnl_file : str, optional
        Path to ``pnl.csv`` recording PnL history.

    Returns
    -------
    str
        Path to the updated ``pnl.csv`` file.
    """
    positions = portfolio.load_portfolio(portfolio_file)
    pnl_df = portfolio.load_pnl(pnl_file)

    if positions.empty:
        return portfolio.save_pnl(pnl_df, pnl_file)

    cur = conn.cursor()
    for _, pos in positions.iterrows():
        symbol = pos["symbol"]
        qty = float(pos["qty"])
        avg_price = float(pos["avg_price"])
        cur.execute(
            "SELECT price FROM realtime_quotes WHERE symbol=? ORDER BY t DESC LIMIT 1",
            (symbol,),
        )
        row = cur.fetchone()
        if row is None:
            continue
        price = float(row[0])
        unrealized = qty * (price - avg_price)
        entry = {
            "date": datetime.utcnow().date().isoformat(),
            "symbol": symbol,
            "unrealized": unrealized,
            "realized": 0.0,
            "total": unrealized,
        }
        pnl_df = pd.concat([pnl_df, pd.DataFrame([entry])], ignore_index=True)

    return portfolio.save_pnl(pnl_df, pnl_file)
