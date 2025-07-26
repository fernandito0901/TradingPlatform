from __future__ import annotations

from pathlib import Path

from trading_platform import backtest


def main() -> None:
    """Run a 30-day backtest using the latest model and features."""
    features = sorted(Path("features").rglob("features.csv"))
    models = sorted(Path("models").rglob("model_*.txt"))
    if not features or not models:
        raise SystemExit("no features or models available")
    backtest.backtest(str(features[-1]), str(models[-1]))


if __name__ == "__main__":
    main()
