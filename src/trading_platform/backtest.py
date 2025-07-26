from __future__ import annotations

from pathlib import Path
import argparse
from trading_platform.reports import REPORTS_DIR

import pandas as pd
import lightgbm as lgb


def backtest(
    features_csv: str,
    model_path: str,
    days: int = 30,
    out_file: str = str(REPORTS_DIR / "pnl.csv"),
) -> str:
    """Run a simple prediction-based backtest and append to an equity curve."""
    df = pd.read_csv(features_csv)
    df["t"] = pd.to_datetime(df["t"])
    df = df.sort_values("t")

    feature_cols = [c for c in df.columns if c not in {"t", "target"}]
    booster = lgb.Booster(model_file=model_path)

    df = df.tail(days + 1)
    df["pred"] = booster.predict(df[feature_cols])
    df["next_close"] = df["close"].shift(-1)
    df["profit"] = ((df["next_close"] - df["close"]) * (df["pred"] > 0.5)).fillna(0)
    df = df.iloc[:-1]
    df["equity"] = df["profit"].cumsum()

    pnl = pd.DataFrame(
        {
            "date": df["t"].dt.date.astype(str),
            "symbol": Path(features_csv).stem.upper(),
            "unrealized": 0.0,
            "realized": df["profit"],
            "total": df["equity"],
        }
    )

    path = Path(out_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        prev = pd.read_csv(path)
        pnl = pd.concat([prev, pnl], ignore_index=True)
    pnl.to_csv(path, index=False)
    return str(path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run backtest with latest model")
    parser.add_argument("features_csv")
    parser.add_argument("model_path")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--out-file", default=str(REPORTS_DIR / "pnl.csv"))
    args = parser.parse_args(argv)
    backtest(args.features_csv, args.model_path, days=args.days, out_file=args.out_file)


if __name__ == "__main__":
    main()
