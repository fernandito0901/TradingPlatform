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
