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
- Drafted plan P006 for POP estimator, paper trading, risk limits, and alert aggregator (tasks T61-T64)
- Added paper trading simulator `simulate.py` with scoreboard PnL logging
- Added `simulate` console script for running the simulator via `pipx` or `python -m`

## 2025-08-19
- Added `strategies.py` with iron condor and call debit spread payoff helpers
- Implemented Monte Carlo POP estimator
- Documented usage in README and moved tasks T57 and T61 to completed
- Added planning document P008 for dashboard and alerting
- Registered tasks T65-T66 for broker stub and portfolio tracker

## 2025-08-20
- Added `generate_strategy_dashboard` to produce `reports/strategies.html` with POP values
- Configuration now accepts `MAX_RISK` for per-strategy limits
- Marked tasks T58 and T63 as completed
- Implemented real-time trade & news alerts with an alert aggregator service
  integrated into `run_daily`. Completed tasks T59 and T64.
- Documented strategy workflow and Slack alerts in README; closed T60.
- Added broker API stub and CLI for placing simulated orders; closed T65.

## 2025-08-21
- Added Flask-based `webapp` command providing a simple web UI
  that prompts for API keys on first run and lets users start the
  daily pipeline or connectivity checks.
## 2025-08-22
- Added plan P009 for full web dashboard
- Registered tasks T68-T72 for expanded web UI and docs

## 2025-08-23
- Expanded webapp with backfill, simulation, and dashboard routes
  and homepage table of recent scoreboard entries. Marked task T69
  complete.

## 2025-08-24
- Added plan P010 for portfolio tracker design and registered tasks T73-T76
  in TASKS.md. Marked T68 complete after documenting the web dashboard design.

## 2025-08-25
- Implemented `portfolio` module with load/save helpers and CLI commands.
  Updated README with usage examples and completed task T74.

## 2025-08-26
- Web UI now shows scoreboard and dashboard links. Portfolio tracker integrated
  into the simulator so trades update `portfolio.csv` and `pnl.csv`. Tasks T70
  and T75 completed.

- Documented web interface usage with example `webapp` command; closed T71.

## 2025-08-27
- Verified webapp and portfolio tests run successfully
  after installing project dependencies. Closed tasks T72 and T76.

## 2025-08-28
- All tests pass across suite after installing project editable. No open tasks.
## 2025-08-29
- Added plan P011 for scheduler and docker-compose deployment.
  Registered tasks T77-T81 in TASKS.md.

## 2025-08-30
- Implemented `scheduler.py` using APScheduler and added CLI entrypoint.
- Added APScheduler dependency and exposed scheduler from package.
- Completed task T78 in TASKS.md.


## 2025-08-31
- Expanded P011 with scheduler architecture and docker-compose details.
- Marked task T77 completed in TASKS.md.

## 2025-09-01
- Added `docker-compose.yml` defining `web` and `scheduler` services.
- README now documents how to build and run both services via docker-compose.

## 2025-09-02
- Webapp can start and stop the scheduler from the browser.
- Added scheduler documentation and CLI usage section.
- Scheduler tests ensure `run_daily` executes on schedule.
- Review complete; merged scheduler features and docs.

## 2025-09-03
- Added plan P012 for portfolio risk metrics and created tasks T82-T86.
- Added `risk_report` CLI for Sharpe and drawdown metrics.
- Added file existence validation and extra test for `risk_report`.
- Expanded plan P012 with risk formulas and scoreboard notes; detailed real-time plan P013 and closed T82.
- Webapp now displays Sharpe ratio and max drawdown on the scoreboard.
- Broker orders automatically update `portfolio.csv`.

## 2025-09-04
- Added `portfolio_stream` module streaming quotes for open positions into the database.
- Alert aggregator now handles position entry and exit messages.
- New CLI `portfolio-stream` starts real-time streaming based on `portfolio.csv`.
- Tasks T87 and T91 completed.
- Review complete; confirmed risk dashboard and trade streaming features.

## 2025-09-05
- Added exit simulation algorithm recording unrealized PnL for open positions.
- Position evaluator engine and CLI implemented with accompanying tests.
- Documented risk workflow, real-time monitoring and evaluator usage in README.

## 2025-09-06
- Fixed recursion error when importing :mod:`trading_platform.scheduler` and
  enabled lazy loading for the new ``evaluator`` module.
- Webapp now listens on ``0.0.0.0`` so the UI is reachable outside the
  container. Host and port can be overridden with ``WEBAPP_HOST`` and
  ``WEBAPP_PORT``.

## 2025-09-07
- Playbook generator now reads feature names from the trained model, avoiding
  LightGBM shape mismatch errors during prediction.

## 2025-09-08
- Missing model features are padded with zeros when generating playbooks so
  LightGBM predictions work even if some columns are absent.

## 2025-09-09
- Training now uses all feature columns by default so new indicators are picked
  up automatically. Updated schemas and README.

## 2025-09-10
- Training aborts early when the feature CSV has no rows, explaining that more
  historical data is required.
- Feature pipeline raises ``ValueError`` if fewer than sixty days of prices are
  available.

## 2025-09-11
- ``run_daily`` now prints recommended trades after generating the playbook to
  the console for quick review.

## 2025-09-12
- Slack alerts now include a formatted table of the day’s trade
  recommendations with probability and momentum details.
- AlertAggregator messages are grouped with bullet points for easier reading.
- Playbook JSON stores prediction components for each trade.

## 2025-09-13
- Web dashboard redesigned with Bootstrap and SocketIO for live trade updates.
- Dashboard auto-loads playbooks, news and portfolio data from local files.
- Charts display feature importance, backtest results and equity curve.

## 2025-09-14
- Dashboard shows watchlist and market overview panels.
- Toast notifications display recent alerts from `reports/alerts.log`.
- Forms for simulation and feature dashboard auto-select the latest features CSV.

## 2025-09-15
- Daily pipeline broadcasts recommended trades via WebSocket so the dashboard
  updates instantly while the run completes.

## 2025-09-16
- Web interface now passes `allow_unsafe_werkzeug=True` so the Flask server runs
  inside Docker without errors.

## 2025-09-17
- Dashboard styling refreshed with Google "Inter" font and dark mode toggle.
- Alerts are deduplicated and include Clear/Mark buttons.
- Recommended trades now show probability bars and auto-refresh via AJAX.
- Scoreboard CSV is created on startup to avoid 404 errors.

## 2025-09-18
- News feed deduplicates headlines per session with Clear/Mark controls.
- Placeholder report files prevent 404 errors for dashboards.

## 2025-09-19
- Added planning doc P016 for delayed Polygon feed and opened tasks T101-T105.

## 2025-09-20
- Added `backtest` CLI and updated `scripts/run_backtest.py` to use the latest
  model and features.

## 2025-09-21
- Polished dashboard layout with Bootstrap grid and Font Awesome icons.
- Sections collapse when empty and news/alert toasts are deduplicated.
- Equity curve chart loads lazily and refreshes every 10 minutes.
- Added `docs/ui_overview.md` and updated README with dashboard overview link.

