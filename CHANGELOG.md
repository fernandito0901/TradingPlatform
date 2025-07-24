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

## 2025-08-05
- Playbook scoring now factors in news sentiment, IV edge, unusual options activity and GARCH spike.

## 2025-08-06
- Added `collector.verify` module for quick API connectivity checks.
- New `run_daily.py` orchestrates data collection, feature generation, model training and playbook creation.
- README documents preflight check and daily pipeline.
## 2025-08-07
- Restructured project into src/ package to conform with AGENTS guidelines.
## 2025-08-08
- Moved features and models packages to project root and added CODE_ATLAS, SCHEMAS, RUNBOOK and WORKFLOW docs.
- Added PLAN_INDEX.md listing all design plans.
- Updated tests to import installed package and refreshed README with project layout notes.
## 2025-08-09
- Added plan index entry for architecture doc and new plan.
- Updated architecture overview to match package restructure.
- Organized planning notes by month and cleaned TASKS.md duplicates.
## 2025-08-10
- Logged planning tasks for automating PLAN_INDEX and versioning architecture docs.
## 2025-08-11
- Planned migration to numbered planning docs and added tasks T44-T46.

## 2025-07-24
- Verified test suite passes with editable install after restructure.
