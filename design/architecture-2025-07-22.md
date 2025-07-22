# Architecture Overview

The project will be organized as a Python package named `collector`.
Core modules:
- `collector/api.py` – HTTP helpers and Polygon REST calls.
- `collector/db.py` – SQLite schema and persistence helpers.
- `collector/cli.py` – argument parsing and configuration loading.
- `collector/stream.py` – WebSocket streaming utilities.
- `collector/main.py` – orchestrates fetch and stream functions.

The existing `market_data_collector.py` will become a thin wrapper around
`collector.main`. Tests will live under `tests/` using `pytest` and will
mock HTTP responses.
