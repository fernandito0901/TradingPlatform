"""Broker API stub for simulated orders."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def place_order(
    symbol: str,
    side: str,
    qty: float,
    price: float,
    out_file: str = "reports/orders.csv",
) -> str:
    """Record a simulated trade in ``out_file``.

    Parameters
    ----------
    symbol : str
        Ticker symbol of the asset.
    side : str
        Either ``"BUY"`` or ``"SELL"``.
    qty : float
        Quantity of the asset to trade.
    price : float
        Execution price.
    out_file : str, optional
        Destination CSV to append the order, by default ``"reports/orders.csv"``.

    Returns
    -------
    str
        Path to the updated CSV file.
    """
    order = {
        "time": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "price": price,
    }
    df = pd.DataFrame([order])
    path = Path(out_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        cur = pd.read_csv(path)
        cur = pd.concat([cur, df], ignore_index=True)
    else:
        cur = df
    cur.to_csv(path, index=False)
    return str(path)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for placing simulated orders."""
    import argparse

    parser = argparse.ArgumentParser(description="Broker API stub")
    parser.add_argument("side", choices=["BUY", "SELL"])
    parser.add_argument("symbol")
    parser.add_argument("qty", type=float)
    parser.add_argument("price", type=float)
    parser.add_argument("--out-file", default="reports/orders.csv")
    args = parser.parse_args(argv)
    place_order(args.symbol, args.side, args.qty, args.price, args.out_file)


if __name__ == "__main__":
    main()
