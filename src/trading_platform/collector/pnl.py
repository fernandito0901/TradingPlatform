"""Compute live portfolio metrics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLS = {"total", "pnl", "profit"}


def update_pnl(path: Path) -> pd.DataFrame | None:
    """Return equity curve DataFrame from ``path``.

    Parameters
    ----------
    path : Path
        CSV file containing PnL data. Column names are matched
        case-insensitively against ``REQUIRED_COLS``.

    Returns
    -------
    pandas.DataFrame | None
        ``None`` if the file is missing or does not contain a recognised PnL
        column. Otherwise a DataFrame with ``equity`` and the PnL column and
        ``date`` if present.
    """

    if not path.exists():
        return None

    df = pd.read_csv(path)
    if df.empty:
        return None

    df.columns = df.columns.str.strip().str.lower()
    col = next((c for c in REQUIRED_COLS if c in df.columns), None)
    if col is None:
        return None

    df["equity"] = df[col].cumsum()

    cols = []
    if "date" in df.columns:
        cols.append("date")
    cols.extend(["equity", col])
    return df[cols]
