# Changelog

## 2025-07-24
- Modularized code into collector package and added argparse CLI.
- Collector now requires the `POLYGON_API_KEY` environment variable.

## 2025-07-25
- Added logging module with `--log-file` and `--log-level` CLI options.
- Implemented incremental OHLCV downloading.
- Added packaging metadata via `pyproject.toml`.
- Created pytest tests for API functions and GitHub Actions CI.

## 2025-07-27
- Added feature engineering pipeline producing SMA and RSI features.
- Implemented baseline LightGBM model training with AUC logging.

## 2025-07-23
- Added optional HTTP caching controlled by `CACHE_TTL` environment variable.

## 2025-07-28
- Implemented playbook generation module producing JSON files under `playbooks/`.

## 2025-07-29
- Documented `POLYGON_API_KEY`, `CACHE_TTL` and logging options in README.

## 2025-07-30
- Added NewsAPI integration storing headlines in `news` table.

## 2025-08-01
- Extended feature pipeline with IV30, HV30, GARCH volatility and news sentiment.
- Model training now returns train/test AUC metrics.
- Added HTML dashboard under `reports/` summarizing AUC scores.
