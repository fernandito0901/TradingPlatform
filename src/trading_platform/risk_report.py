"""Risk metrics reporting utilities."""

from pathlib import Path
from . import REPORTS_DIR

import pandas as pd


def risk_metrics(scoreboard_csv: str) -> pd.DataFrame:
    """Return cumulative Sharpe ratio and max drawdown.

    Parameters
    ----------
    scoreboard_csv : str
        CSV file produced by :func:`trading_platform.reports.scoreboard.update_scoreboard` and
        containing ``pnl`` values.

    Returns
    -------
    pandas.DataFrame
        DataFrame with ``date``, ``sharpe`` and ``max_drawdown`` columns.
    """
    path = Path(scoreboard_csv)
    if not path.exists():
        raise FileNotFoundError(scoreboard_csv)

    df = pd.read_csv(path)
    if "pnl" not in df.columns:
        raise ValueError("pnl column required in scoreboard")

    returns = df["pnl"].astype(float)
    mean = returns.expanding().mean()
    std = returns.expanding().std(ddof=0).replace(0, pd.NA)
    sharpe = (mean / std).fillna(0)

    cum_pnl = returns.cumsum()
    running_max = cum_pnl.cummax()
    drawdown = cum_pnl - running_max
    max_dd = drawdown.expanding().min()

    out = df[["date"]].copy()
    out["sharpe"] = sharpe
    out["max_drawdown"] = max_dd
    return out


def main(argv: list[str] | None = None) -> int:
    """CLI entry point printing risk metrics."""
    import argparse

    parser = argparse.ArgumentParser(description="Compute risk metrics")
    parser.add_argument(
        "--scoreboard",
        default=str(REPORTS_DIR / "scoreboard.csv"),
        help="Path to scoreboard CSV",
    )
    parser.add_argument(
        "--out-file",
        help="Optional destination CSV to write metrics",
    )
    args = parser.parse_args(argv)

    metrics = risk_metrics(args.scoreboard)
    if args.out_file:
        Path(args.out_file).parent.mkdir(parents=True, exist_ok=True)
        metrics.to_csv(args.out_file, index=False)
    else:
        print(metrics.to_csv(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
