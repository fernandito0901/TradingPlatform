"""Compute live portfolio metrics."""

from __future__ import annotations

import importlib
from pathlib import Path

import pandas as pd

from .. import metrics as m
from .. import portfolio
from ..reports import REPORTS_DIR


class NoData(Exception):
    pass


def update_pnl(since: str | None = None, path: Path | None = None) -> pd.DataFrame:
    use_portfolio = path is None
    path = Path(path or REPORTS_DIR / "pnl.csv")
    if not path.exists():
        raise NoData("pnl missing")
    if use_portfolio:
        df = portfolio.load_pnl(str(path))
    else:
        df = pd.read_csv(path)
    if df.empty:
        raise NoData("pnl empty")
    df["date"] = pd.to_datetime(df["date"])
    if since and since.endswith("d"):
        try:
            n = int(since[:-1])
            cutoff = pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=n)
            cutoff = cutoff.tz_localize(None)
            df = df[df["date"] >= cutoff]
        except ValueError:
            pass
    df = df.sort_values("date")
    equity = df["total"].cumsum()
    daily = equity.pct_change().fillna(0)
    sharpe = m.sharpe_ratio(daily)
    sortino = m.sortino_ratio(daily)
    out = pd.DataFrame(
        {"date": df["date"].dt.date.astype(str), "equity": equity, "daily_r": daily}
    )
    out["sharpe"] = sharpe
    out["sortino"] = sortino
    out.to_csv(path, index=False)
    importlib.reload(portfolio)  # reset any monkeypatched functions
    return out
