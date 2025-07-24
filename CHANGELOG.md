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
- Added UOA, IV edge and garch spike features to feature pipeline.
- Added GitHub Actions workflow running `black --check` and `pytest -q` on pull requests.
## 2025-08-12
- Added Slack notifier and integrated notifications into `run_daily.py`.

## 2025-07-24
- Verified test suite passes with editable install after restructure.
## 2025-08-13
- Added historical backfill and data quality utilities under `collector` package.
- README documents the new commands.
- Added Dockerfile and run_pipeline.sh for containerized execution.
- README covers Docker usage.
## 2025-08-15
- Moved architecture docs to `design/architecture/` with new `ARCH_INDEX.md`.
- Consolidated dated planning notes into `planning/archive.md`.
- Created numbered planning system starting with `design/plans/P001.md`.
- Updated scripts and README references to use the numbered plans.

- Drafted planning document P002 and outlined tasks T47-T50.
- Drafted planning document P003 covering tasks T51-T53.
- Implemented async collector API and `.env` loader with tests.

## 2025-08-16
- Added `collector.stream_async` for asynchronous WebSocket streaming and updated
  README documentation.
- Tests cover reconnect behavior and dependency list includes `websockets`.

## 2025-08-17
- Added 5-fold cross-validation mode in `models.train` with average AUC.
- Dashboard now reports **CV AUC** when provided.
- Introduced `reports.scoreboard` to track daily playbook results.
- Created interactive Plotly feature dashboard.
## 2025-08-18
- Drafted planning document P004 describing unified Config dataclass tasks
- Added tasks T54-T56 for config dataclass design, refactor, and documentation
- Implemented Config dataclass and refactored `run_daily` and collector entry point
