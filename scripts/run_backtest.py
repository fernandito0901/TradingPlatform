from __future__ import annotations

from pathlib import Path

from trading_platform import backtest, metrics
import pandas as pd


def main() -> None:
    """Run a 30-day backtest using the latest model and features."""
    features = sorted(Path("features").rglob("features.csv"))
    models = sorted(Path("models").rglob("model_*.txt"))
    if not features or not models:
        raise SystemExit("no features or models available")
    csv = backtest.backtest(str(features[-1]), str(models[-1]))
    df = pd.read_csv(csv)
    sharpe = metrics.sharpe_ratio(df["total"].astype(float).diff().dropna())
    print(f"Sharpe {sharpe:.2f}")
    if sharpe < 0.8:
        raise SystemExit("Sharpe too low")


if __name__ == "__main__":
    main()
