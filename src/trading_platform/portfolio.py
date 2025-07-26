"""Utilities for tracking simulated trades and portfolio PnL."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from trading_platform.reports import REPORTS_DIR

import pandas as pd

PORTFOLIO_FILE = str(REPORTS_DIR / "portfolio.csv")
PNL_FILE = str(REPORTS_DIR / "pnl.csv")


def load_portfolio(path: str = PORTFOLIO_FILE) -> pd.DataFrame:
    """Load portfolio CSV or return empty DataFrame."""
    file = Path(path)
    if file.exists():
        return pd.read_csv(file)
    return pd.DataFrame(columns=["symbol", "strategy", "qty", "avg_price", "opened_at"])


def save_portfolio(df: pd.DataFrame, path: str = PORTFOLIO_FILE) -> str:
    """Persist portfolio to CSV and return the file path."""
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file, index=False)
    return str(file)


def load_pnl(path: str = PNL_FILE) -> pd.DataFrame:
    """Load PnL history or return empty DataFrame."""
    file = Path(path)
    if file.exists():
        return pd.read_csv(file)
    return pd.DataFrame(columns=["date", "symbol", "unrealized", "realized", "total"])


def save_pnl(df: pd.DataFrame, path: str = PNL_FILE) -> str:
    """Persist PnL history to CSV."""
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file, index=False)
    return str(file)


def record_trade(
    symbol: str,
    strategy: str,
    qty: float,
    price: float,
    portfolio_file: str = PORTFOLIO_FILE,
) -> str:
    """Add or update a trade in the portfolio."""
    df = load_portfolio(portfolio_file)
    now = datetime.utcnow().isoformat()
    if symbol in df["symbol"].values:
        row = df[df["symbol"] == symbol].iloc[0]
        new_qty = row["qty"] + qty
        avg_price = (row["avg_price"] * row["qty"] + price * qty) / new_qty
        if new_qty == 0:
            df = df[df["symbol"] != symbol]
        else:
            df.loc[df["symbol"] == symbol, ["qty", "avg_price"]] = [new_qty, avg_price]
    else:
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        {
                            "symbol": symbol,
                            "strategy": strategy,
                            "qty": qty,
                            "avg_price": price,
                            "opened_at": now,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return save_portfolio(df, portfolio_file)


def close_position(
    symbol: str,
    price: float,
    portfolio_file: str = PORTFOLIO_FILE,
    pnl_file: str = PNL_FILE,
) -> str:
    """Close a position and record realized PnL."""
    df = load_portfolio(portfolio_file)
    if symbol not in df["symbol"].values:
        raise ValueError(f"no position for {symbol}")
    row = df[df["symbol"] == symbol].iloc[0]
    qty = row["qty"]
    realized = qty * (price - row["avg_price"])
    df = df[df["symbol"] != symbol]
    save_portfolio(df, portfolio_file)

    pnl = load_pnl(pnl_file)
    entry = {
        "date": datetime.utcnow().date().isoformat(),
        "symbol": symbol,
        "unrealized": 0.0,
        "realized": realized,
        "total": realized,
    }
    pnl = pd.concat([pnl, pd.DataFrame([entry])], ignore_index=True)
    save_pnl(pnl, pnl_file)
    return str(pnl_file)


def main(argv: list[str] | None = None) -> None:
    """CLI for viewing and updating the portfolio."""
    import argparse

    parser = argparse.ArgumentParser(description="Portfolio tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    show_p = sub.add_parser("show", help="Display open positions")
    show_p.add_argument("--file", default=PORTFOLIO_FILE)

    close_p = sub.add_parser("close", help="Close a position")
    close_p.add_argument("symbol")
    close_p.add_argument("price", type=float)
    close_p.add_argument("--portfolio-file", default=PORTFOLIO_FILE)
    close_p.add_argument("--pnl-file", default=PNL_FILE)

    args = parser.parse_args(argv)
    if args.cmd == "show":
        df = load_portfolio(args.file)
        if df.empty:
            print("No open positions")
        else:
            print(df.to_string(index=False))
    elif args.cmd == "close":
        close_position(args.symbol, args.price, args.portfolio_file, args.pnl_file)


if __name__ == "__main__":
    main()
