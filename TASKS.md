# Open Tasks
# (All tasks should have unique IDs in ascending order)

- [T100] Review UI redesign · Acceptance: Reviewer approves new interface documentation.
- [T101] Describe delayed Polygon feed architecture · Acceptance: planning document P016 outlines configuration and process.
- [T102] Implement delayed_stream.py · Acceptance: quotes saved to market_data.db in real time.
- [T103] Connect delayed stream to pipeline · Acceptance: webapp shows live trade ideas while training.
- [T104] Tests for delayed feed and auto start · Acceptance: pytest covers stream integration and pipeline kickoff.
- [T105] Review delayed feed implementation · Acceptance: README updated and PR approved by Reviewer.

# Completed Tasks
- [T85] Document risk workflow · Acceptance: README explains risk_report usage and risk limits. · Completed by Reviewer on 2025-09-05
- [T99] Document dashboard usage · Acceptance: README screenshots and description. · Completed by Synthesizer on 2025-09-21
- [T88] Position evaluator engine · Acceptance: open positions monitored and exit signals computed. · Completed by Coder on 2025-09-05
- [T90] Exit simulation algorithm · Acceptance: simulator records hypothetical exits and updates PnL. · Completed by Modeler on 2025-09-05
- [T92] Document real-time monitoring · Acceptance: README explains live evaluation and alert workflow. · Completed by Reviewer on 2025-09-05
- [T93] Evaluator CLI · Acceptance: `evaluator.py` runs continuous evaluation loop and records exit signals. · Completed by Coder on 2025-09-05
- [T94] Evaluator tests · Acceptance: pytest verifies signals trigger and PnL updates. · Completed by Tester on 2025-09-05
- [T95] Document evaluator usage · Acceptance: README includes section on running the evaluator and interpreting output. · Completed by Reviewer on 2025-09-05
- [T86] Risk report tests · Acceptance: pytest covers risk calculations and dashboard output. · Completed by Tester on 2025-09-05
- [T87] Real-time streaming for portfolio symbols · Acceptance: quotes for held symbols update every minute and log to database. · Completed by DataCollector on 2025-09-04
- [T91] Real-time alert notifications · Acceptance: user notified via Slack when entry or exit triggers occur. · Completed by DataCollector on 2025-09-04
- [T96] Modern dashboard design · Acceptance: plan P015 outlines new layout and API routes. · Completed by Planner on 2025-09-10
- [T97] Implement watchlist and alert streaming · Acceptance: webapp shows watchlist, toasts, and auto-loaded files. · Completed by Coder on 2025-09-10
- [T98] Update webapp tests for new endpoints · Acceptance: pytest covers watchlist and alerts API. · Completed by Tester on 2025-09-10
- [T96] Modern dashboard design · Acceptance: plan P015 outlines new layout and API routes. · Completed by Planner on 2025-09-10
- [T97] Implement watchlist and alert streaming · Acceptance: webapp shows watchlist, toasts, and auto-loaded files. · Completed by Coder on 2025-09-10
- [T98] Update webapp tests for new endpoints · Acceptance: pytest covers watchlist and alerts API. · Completed by Tester on 2025-09-10
- [T72] Webapp tests · Acceptance: pytest covers new routes and setup flow · Completed by Tester on 2025-08-27
- [T76] Portfolio tests · Acceptance: pytest validates trade recording and PnL calculations · Completed by Tester on 2025-08-27
- [T77] Scheduler architecture plan · Acceptance: design doc P011 outlines scheduler and compose setup · Completed by Planner on 2025-08-31
- [T46] Update references for new planning layout · Acceptance: README and automation scripts point to numbered plans · Completed by Planner on 2025-08-14
- [T45] Adopt numbered plan docs · Acceptance: new notes saved as `design/plans/P001.md` etc. with sequential index · Completed by Planner on 2025-08-14
- [T44] Consolidate historical plans · Acceptance: dated notes summarized in `planning/archive.md` and old files removed · Completed by Planner on 2025-08-14
- [T43] Versioned architecture docs · Acceptance: move architecture notes to `design/architecture/` with index and update links · Completed by Planner on 2025-08-14
- [T41] Automate planning index · Acceptance: script regenerates `design/PLAN_INDEX.md` from plan files; CI runs it · Completed by Coder on 2025-08-14
- [T1] Secure API Key handling · Acceptance: collector fails to start without `POLYGON_API_KEY`; README updated · Completed by Coder on 2025-07-22
- [T3] Introduce configuration module for CLI args · Acceptance: script accepts symbols list, database path, and real-time flag via argparse · Completed by Coder on 2025-07-22
- [T4] Modularize project into `collector/` package · Acceptance: create `collector/api.py`, `collector/db.py`, `collector/cli.py`, `collector/stream.py`, and update main script to import these modules · Completed by Coder on 2025-07-22
- [T5] Write architecture overview · Acceptance: `design/architecture-2025-07-22.md` describes modules and data flow · Completed by Planner on 2025-07-22
- [T11] Implement HTTP caching layer · Acceptance: repeated API calls within TTL skip network request; TTL set via `CACHE_TTL` env var; tests updated · Completed by Coder on 2025-07-23
- [T13] Feature engineering pipeline · Acceptance: `features/{date}/features.csv` produced with SMA and RSI columns; unit test validates shape · Completed by Modeler on 2025-07-23
- [T14] Baseline model training · Acceptance: LightGBM model saved under `models/`; AUC logged in `NOTES.md`; tests cover training function · Completed by Modeler on 2025-07-23
- [T12] Integrate NewsAPI for headlines · Acceptance: `collector.api` stores top articles in `news` table; schema documented · Completed by DataCollector on 2025-07-30
- [T9] Document environment variables · Acceptance: README explains `POLYGON_API_KEY` and logging config section · Completed by Reviewer on 2025-07-29
- [T10] Add WebSocket tests for stream_quotes · Acceptance: mocked server verifies reconnect logic; `pytest -q` passes · Completed by Tester on 2025-07-29
- [T16] Extend feature pipeline with IV/HV and GARCH σ · Acceptance: `compute_features` outputs `iv30`, `hv30`, `garch_sigma`; tests updated · Completed by Modeler on 2025-08-01
- [T17] Cross-validate LightGBM model · Acceptance: `models.train` returns train/test AUC; tests cover new logic · Completed by Modeler on 2025-08-01
