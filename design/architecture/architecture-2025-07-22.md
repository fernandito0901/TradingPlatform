# Architecture Overview - 2025-07-22

The project exposes a package named `trading_platform` inside `src/`. Collector
logic resides under `trading_platform.collector` while feature engineering and
model training live in top-level `features/` and `models/` packages. Thin
wrapper modules under `src/trading_platform/features` and
`src/trading_platform/models` re-export these packages so existing imports keep
working.

Key modules:
- `trading_platform.collector.api` – REST helpers for Polygon endpoints.
- `trading_platform.collector.db` – SQLite schema and persistence helpers.
- `trading_platform.collector.stream` – WebSocket utilities.
- `features.pipeline` – feature engineering steps.
- `models.train` – LightGBM training entry point.

`market_data_collector.py` simply calls into `trading_platform.collector.main`.
Tests under `tests/` rely on an editable install of the package and mock network
requests with pytest fixtures.
