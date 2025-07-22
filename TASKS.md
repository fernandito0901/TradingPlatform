# Open Tasks

- [T1] **Done** – Secure API Key handling · Acceptance: collector fails to start without `POLYGON_API_KEY`; README updated · Assignee: Coder
- [T2] Add pytest-based tests for data fetch functions · Acceptance: tests cover `fetch_ohlcv` and `fetch_minute_bars` using mocked responses; `pytest -q` passes · Assignee: Tester
- [T3] Introduce configuration module for CLI args · Acceptance: script accepts symbols list, database path, and real-time flag via argparse · Assignee: Coder
- [T4] Modularize project into `collector/` package · Acceptance: create `collector/api.py`, `collector/db.py`, `collector/cli.py`, `collector/stream.py`, and update main script to import these modules · Assignee: Coder
- [T5] Write architecture overview · Acceptance: `design/architecture-2025-07-22.md` describes modules and data flow · Assignee: Planner
