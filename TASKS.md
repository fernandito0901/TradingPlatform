# Open Tasks

- [T19] Update playbook scoring rule · Acceptance: `generate_playbook` uses news_sent, IV_edge, UOA and garch_spike; tests validate weighting · Assignee: Synthesizer
- [T21] Continuous integration workflow · Acceptance: GitHub Actions runs `black --check` and `pytest -q` on pull requests · Assignee: Coder
- [T22] Slack notification alerts · Acceptance: pipeline sends Slack message after playbook generation and on errors; config documented · Assignee: Coder
- [T23] Historical data backfill script · Acceptance: `collector.backfill` downloads missing bars for a date range; unit test validates row count · Assignee: DataCollector
- [T25] Docker packaging · Acceptance: `Dockerfile` and `run_pipeline.sh` enable one-command execution; instructions in README · Assignee: Coder
- [T26] Review modeling updates · Acceptance: confirm docs and tests for new features, run `pytest -q` and squash-merge · Assignee: Reviewer
- [T29] UOA indicator · Acceptance: `features.pipeline` outputs `uoa` column computed from option volume vs. 30‑day average; tests validate calculation · Assignee: Modeler
- [T30] IV edge & garch spike features · Acceptance: `features.pipeline` includes `iv_edge` and `garch_spike` columns; tests confirm formulas · Assignee: Modeler
- [T32] Data quality report script · Acceptance: `collector.quality` outputs per-symbol missing day count and null stats; unit test verifies output · Assignee: DataCollector
- [T41] Automate planning index · Acceptance: script regenerates `design/PLAN_INDEX.md` from plan files; CI runs it · Assignee: Coder
- [T42] Validate plan headers · Acceptance: CI fails if a plan's heading doesn't match its filename; script checks all docs · Assignee: Tester
- [T43] Versioned architecture docs · Acceptance: move architecture notes to `design/architecture/` with index and update links · Assignee: Planner
- [T44] Consolidate historical plans · Acceptance: dated notes summarized in `planning/archive.md` and old files removed · Assignee: Planner
- [T45] Adopt numbered plan docs · Acceptance: new notes saved as `design/plans/P001.md` etc. with sequential index · Assignee: Planner
- [T46] Update references for new planning layout · Acceptance: README and automation scripts point to numbered plans · Assignee: Coder

# Completed Tasks

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
- [T18] Add news sentiment feature · Acceptance: `features.csv` includes `news_sent` column computed from collected headlines; tests updated · Completed by Modeler on 2025-08-01
- [T24] Performance metrics dashboard · Acceptance: `reports/dashboard.html` plots model AUC and trade stats; README links to sample · Completed by Modeler on 2025-08-01
- [T20] Daily orchestration script · Acceptance: `run_daily.py` executes collection, features, training and playbook; README updated; tests cover CLI · Completed by Coder on 2025-08-06
- [T27] Connectivity test command · Acceptance: `collector.verify` fetches OHLCV and option data for up to 5 symbols using API keys provided via CLI and prints a summary; README documents usage · Completed by DataCollector on 2025-08-06
- [T28] Tests for connectivity command · Acceptance: pytest covers success and failure paths for `collector.verify` with mocked API responses · Completed by Tester on 2025-08-06
- [T31] README update for verify command · Acceptance: README section demonstrates `python -m collector.verify` with API keys via CLI · Completed by Reviewer on 2025-08-06
- [T33] Preflight connectivity check · Acceptance: `run_daily.py` invokes `collector.verify` and aborts on failure; tests cover both paths · Completed by Coder on 2025-08-06
- [T34] Update test imports for new package layout · Acceptance: tests run without manual `sys.path` modifications by installing `trading_platform` via `pip install -e .` · Completed by Tester on 2025-08-08
- [T35] Refresh documentation for restructure · Acceptance: README and design docs describe top-level `features` and `models` packages; examples updated · Completed by Reviewer on 2025-08-08
- [T36] Create planning document index · Acceptance: `design/PLAN_INDEX.md` lists all plan files chronologically; README links to it · Completed by Planner on 2025-08-08
- [T37] Normalize headers in early plans · Acceptance: `plan-2025-07-22.md` uses `Planning Notes - YYYY-MM-DD` heading to match others · Completed by Planner on 2025-08-08
- [T38] Update architecture overview · Acceptance: `design/architecture-2025-07-22.md` reflects current module layout with root packages and wrappers · Completed by Planner on 2025-08-09
- [T39] Organize plan documents by month · Acceptance: move plans into `design/2025-*` subfolders and update PLAN_INDEX · Completed by Planner on 2025-08-09
- [T40] Clean up TASKS.md sections · Acceptance: remove duplicated "Planned Tasks" and ensure all open tasks are listed once · Completed by Planner on 2025-08-09
