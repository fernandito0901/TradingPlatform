#!/usr/bin/env python
"""Generate PnL report from trades and current equity."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from trading_platform.metrics import sharpe_ratio, sortino_ratio


def generate(trades_csv: str, equity: float, out_file: str) -> str:
    trades = pd.read_csv(trades_csv)
    if trades.empty:
        df = pd.DataFrame(columns=["date", "equity", "pnl"])
    else:
        trades["date"] = pd.to_datetime(trades["date"]).dt.date
        pnl = trades.groupby("date")["pnl"].sum()
        equity_series = pnl.cumsum() + equity
        df = pd.DataFrame(
            {"date": pnl.index.astype(str), "equity": equity_series, "pnl": pnl}
        )
    if len(df) < 2:
        df.to_csv(out_file, index=False)
        return out_file
    daily_r = df["pnl"].pct_change().fillna(0)
    df["sharpe"] = sharpe_ratio(daily_r)
    df["sortino"] = sortino_ratio(daily_r)
    df.to_csv(out_file, index=False)
    return out_file


def main() -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("trades")
    p.add_argument("equity", type=float)
    p.add_argument("--out", default="reports/pnl.csv")
    args = p.parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    generate(args.trades, args.equity, args.out)


if __name__ == "__main__":
    main()
