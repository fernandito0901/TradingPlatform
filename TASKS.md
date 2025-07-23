# Open Tasks

- [T19] Update playbook scoring rule · Acceptance: `generate_playbook` uses news_sent, IV_edge, UOA and garch_spike; tests validate weighting · Assignee: Synthesizer
- [T20] Daily orchestration script · Acceptance: `run_daily.py` executes collection, features, training and playbook; README updated; tests cover CLI · Assignee: Coder
- [T21] Continuous integration workflow · Acceptance: GitHub Actions runs `black --check` and `pytest -q` on pull requests · Assignee: Coder
- [T22] Slack notification alerts · Acceptance: pipeline sends Slack message after playbook generation and on errors; config documented · Assignee: Coder
- [T23] Historical data backfill script · Acceptance: `collector.backfill` downloads missing bars for a date range; unit test validates row count · Assignee: DataCollector
- [T25] Docker packaging · Acceptance: `Dockerfile` and `run_pipeline.sh` enable one-command execution; instructions in README · Assignee: Coder
- [T26] Review modeling updates · Acceptance: confirm docs and tests for new features, run `pytest -q` and squash-merge · Assignee: Reviewer


# Planned Tasks
- [T19] Update playbook scoring rule · Acceptance: `generate_playbook` uses news_sent, IV_edge, UOA and garch_spike; tests validate weighting · Assignee: Synthesizer
- [T20] Daily orchestration script · Acceptance: `run_daily.py` executes collection, features, training and playbook; README updated; tests cover CLI · Assignee: Coder
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

