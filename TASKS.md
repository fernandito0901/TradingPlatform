# Open Tasks

- [T2] Add pytest-based tests for data fetch functions · Acceptance: tests cover `fetch_ohlcv` and `fetch_minute_bars` using mocked responses; `pytest -q` passes · Assignee: Tester
- [T6] Add logging module · Acceptance: logs written to a user-specified file with configurable level; CLI flag `--log-file` available · Assignee: Coder
- [T7] Setup CI workflow · Acceptance: `.github/workflows/ci.yml` runs `black --check` and `pytest -q` on push · Assignee: Tester
- [T8] Package project for distribution · Acceptance: `pyproject.toml` defines `collector` package and entry point; `pip install -e .` works · Assignee: Coder
- [T9] Document environment variables · Acceptance: README explains `POLYGON_API_KEY` and logging config section · Assignee: Reviewer

# Completed Tasks

- [T1] Secure API Key handling · Acceptance: collector fails to start without `POLYGON_API_KEY`; README updated · Completed by Coder on 2025-07-22
- [T3] Introduce configuration module for CLI args · Acceptance: script accepts symbols list, database path, and real-time flag via argparse · Completed by Coder on 2025-07-22
- [T4] Modularize project into `collector/` package · Acceptance: create `collector/api.py`, `collector/db.py`, `collector/cli.py`, `collector/stream.py`, and update main script to import these modules · Completed by Coder on 2025-07-22
- [T5] Write architecture overview · Acceptance: `design/architecture-2025-07-22.md` describes modules and data flow · Completed by Planner on 2025-07-22
