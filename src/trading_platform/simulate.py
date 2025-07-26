"""Simple paper trading simulator."""

from pathlib import Path

import pandas as pd

from trading_platform.reports.scoreboard import update_scoreboard
from trading_platform import portfolio
from trading_platform.reports import REPORTS_DIR


STRATEGIES = ["buy_hold"]


def simulate(
    features_csv: str,
    strategy: str = "buy_hold",
    capital: float = 10_000.0,
    out_file: str = str(REPORTS_DIR / "scoreboard.csv"),
    portfolio_file: str = portfolio.PORTFOLIO_FILE,
    pnl_file: str = portfolio.PNL_FILE,
    symbol: str | None = None,
) -> str:
    """Simulate a strategy on historical prices and record PnL.

    Parameters
    ----------
    features_csv : str
        Features CSV containing a ``close`` column.
    strategy : str, optional
        Strategy name, by default ``"buy_hold"``.
    capital : float, optional
        Starting capital for the trade, by default ``10000``.
    out_file : str, optional
        Scoreboard CSV path, by default ``REPORTS_DIR / 'scoreboard.csv'``.

    Returns
    -------
    str
        Path to the scoreboard CSV after update.
    """
    df = pd.read_csv(features_csv)
    if "close" not in df.columns:
        raise ValueError("close column required")

    if symbol is None:
        symbol = Path(features_csv).stem.upper()

    if strategy == "buy_hold":
        entry_price = df["close"].iloc[0]
        shares = capital / entry_price
        portfolio.record_trade(
            symbol,
            strategy,
            shares,
            entry_price,
            portfolio_file=portfolio_file,
        )
        exit_price = df["close"].iloc[-1]
        pnl = shares * (exit_price - entry_price)
        portfolio.close_position(
            symbol,
            exit_price,
            portfolio_file=portfolio_file,
            pnl_file=pnl_file,
        )
    else:
        raise ValueError(f"unknown strategy: {strategy}")

    result = Path(features_csv)
    scoreboard = update_scoreboard(str(result), 0.0, pnl=pnl, out_file=out_file)
    return scoreboard


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Paper trading simulator")
    parser.add_argument("features_csv")
    parser.add_argument("--strategy", default="buy_hold", choices=STRATEGIES)
    parser.add_argument("--capital", type=float, default=10_000.0)
    parser.add_argument("--portfolio-file", default=portfolio.PORTFOLIO_FILE)
    parser.add_argument("--pnl-file", default=portfolio.PNL_FILE)
    parser.add_argument("--symbol")
    args = parser.parse_args(argv)
    simulate(
        args.features_csv,
        args.strategy,
        args.capital,
        portfolio_file=args.portfolio_file,
        pnl_file=args.pnl_file,
        symbol=args.symbol,
    )


if __name__ == "__main__":
    main()
