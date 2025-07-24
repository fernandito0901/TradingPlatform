# Market Data Collector

This script polls the [Polygon](https://polygon.io) REST API to collect
historical bars, minute aggregates, delayed real‑time quotes and option
chain snapshots for a given symbol. The collector also stores basic
fundamental data, recent corporate actions and a 50‑day simple moving
average. All results are cached in a local SQLite database.

## Requirements

- Python 3.8+
- `requests` library
- `websocket-client` library

Install dependencies with the same Python interpreter you use to run the
collector:

```bash
pip install -e .
python3 -m pip install -r requirements.txt
```

## Project Layout

Core collector code lives under `src/trading_platform`. Feature engineering and
model training packages are located at the repository root under `features/` and
`models/`. Wrapper modules under `src/trading_platform/features` and
`src/trading_platform/models` re-export these packages for backward
compatibility.

## Configuration

The collector relies on a couple of environment variables and optional
command‑line flags. These are merged into a single ``Config`` dataclass
loaded via ``trading_platform.load_config``:

- **`POLYGON_API_KEY`**: API key required for all REST and WebSocket requests.
- **`CACHE_TTL`**: Time‑to‑live in seconds for HTTP response caching. Set to
  `0` to disable caching.
- **`SLACK_WEBHOOK_URL`**: Incoming webhook for pipeline notifications.
- **`MAX_RISK`**: Comma-separated per-strategy limits like ``call=100,condor=50``.
- `.env` files are loaded automatically if present so secrets can be stored locally.

Logging can be directed to a file and the verbosity adjusted using the
`--log-file` and `--log-level` arguments, respectively.

## Usage

Export your `POLYGON_API_KEY` and set any optional variables described in the
[Configuration](#configuration) section. Then run the script with optional
arguments:

```bash
python -m trading_platform.market_data_collector \
  --symbols AAPL,MSFT --stream --realtime --db-file mydata.db
```

The script incrementally fetches OHLCV data, retrieving only new days while ensuring the last 60 days are present, the most recent minute
aggregates, a delayed quote from the snapshot endpoint, and the weekly option chain for the default symbol `AAPL`. Basic fundamentals, recent split history and a 50-day SMA are stored as well.

Collected data is stored in `market_data.db`.

To stream trades and quotes continuously, pass the `--stream` flag. By
default the collector uses Polygon's **delayed** WebSocket, which is available
on the Starter plan. You can also request the real-time feed with the
`--realtime` flag. If the request fails due to insufficient permissions, the
collector automatically falls back to the delayed feed.

```bash
python -m trading_platform.market_data_collector --symbols AAPL --stream
```

To stream multiple tickers, separate them with commas and optionally pass the
`realtime` flag to use the live feed instead of the delayed one:

```bash
python -m trading_platform.market_data_collector \
  --symbols AAPL,MSFT --stream --realtime
```

The client waits for the connection to be authenticated before subscribing to trade and quote channels. If a `not authorized` error is returned when using the real-time feed, the collector automatically reconnects using the delayed WebSocket. The feed prints trade and quote data until interrupted.

An asynchronous streaming helper is available in ``trading_platform.collector.stream_async``. It uses the ``websockets`` package and can be combined with the async API for fully non-blocking pipelines.

## Logging
Logs default to stdout. Use `--log-file` to write to a specific path and
`--log-level` to choose the log severity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

## Starter Plan Compatibility

The collector uses endpoints that are accessible with Polygon's **Stocks** and
**Options** starter plans. Quotes and the default WebSocket stream are delayed
by 15 minutes. Option snapshots may omit bid/ask data. Additional fundamentals,
corporate actions and technical indicators are fetched for future use when
available.

## Reports

Model training metrics are written to `reports/dashboard.html`. Open this file
in a browser to view recent AUC scores. Pass ``cv=True`` to
``models.train`` to compute a 5-fold average AUC that appears as **CV AUC**.
Call ``generate_feature_dashboard`` with the features CSV to produce
`reports/feature_dashboard.html` for interactive exploration of feature
distributions. Historical results are stored in `reports/scoreboard.csv`.
Use ``generate_strategy_dashboard`` to write `reports/strategies.html` summarizing POP for available trades.

## Preflight Connectivity Check
Run a quick smoke test before the full pipeline to validate your API keys:

```bash
python -m collector.verify --symbols AAPL,MSFT --polygon-key YOUR_KEY --news-key YOUR_KEY
```

The command fetches a small sample of OHLCV bars and option chains and exits non-zero on failure.

## Daily Pipeline
Use `run_daily.py` to execute data collection, feature generation, model training and playbook creation in one step. The script accepts the same options as
``load_config``:

```bash
python run_daily.py --symbols AAPL,MSFT --db-file market_data.db
```

The script aborts if the preflight connectivity check fails.
If ``SLACK_WEBHOOK_URL`` is set, a message is posted on success or failure.
Large trades and breaking news are detected during execution and aggregated into
a Slack alert if ``SLACK_WEBHOOK_URL`` is configured.

## Data Utilities

Use the helper commands below to maintain the local database.

### Backfill Historical Bars

Fetch missing daily bars for a specific range:

```bash
python -m collector.backfill AAPL 2025-01-01 2025-01-31 --db-file market_data.db
```

### Data Quality Report

Get per-symbol stats on missing days and null values:

```bash
python -m collector.quality --db-file market_data.db
```

### Paper Trading Simulator

Run a simple buy‑and‑hold backtest and record profits to the scoreboard:

```bash
simulate data/features.csv --strategy buy_hold --capital 10000
```

The CSV at `reports/scoreboard.csv` tracks daily AUC and optional PnL values.
Simulated trades are also logged in `reports/portfolio.csv` and realized
profits appended to `reports/pnl.csv`.

### Broker API Stub

Place simulated orders from the command line using the broker stub:

```bash
broker BUY AAPL 1 100 --out-file reports/orders.csv
```

Each order is appended to `reports/orders.csv` with a timestamp.

### Portfolio Tracker

Manage open positions and record realized profits:

```bash
portfolio show --file reports/portfolio.csv
portfolio close AAPL 150 --portfolio-file reports/portfolio.csv --pnl-file reports/pnl.csv
```

Closing a position updates `reports/pnl.csv` so dashboards can track PnL over time.

### Web Interface

Launch a local web UI for running commands:

```bash
webapp
```

On first launch, the page prompts for API keys and saves them to `.env`.
After setup you can run the daily pipeline or connectivity checks with
buttons on the homepage. You can also backfill historical bars, run simulations, and generate feature or strategy dashboards directly from the site. Recent results from `reports/scoreboard.csv` are displayed with links to all reports.

### Strategy Workflow

Use the strategy helpers and dashboard generator to evaluate trades:

```python
from trading_platform import strategies
from reports.strategy_dashboard import generate_strategy_dashboard

strategies_data = [
    {
        "name": "Call Debit Spread",
        "payoff": lambda s: strategies.call_debit_spread_payoff(s, 100, 110, 5),
        "price": 100,
    }
]
generate_strategy_dashboard(strategies_data)
```

The HTML report `reports/strategies.html` lists probability of profit (POP) for
each trade. When `SLACK_WEBHOOK_URL` is set, large trades and breaking news are
aggregated into a Slack alert during `run_daily.py` execution.

### Option Strategies and POP

Use the `strategies` module to evaluate spreads and estimate probability of
profit. Example:

```python
from trading_platform import strategies

# payoff of a call debit spread
profit = strategies.call_debit_spread_payoff(120, 100, 110, 5)

# probability of profit via Monte Carlo
pop = strategies.pop(
    lambda s: strategies.call_debit_spread_payoff(s, 100, 110, 5),
    price=100,
)
```

## Docker Usage

Build the container and run the full pipeline in one step:

```bash
docker build -t trading-platform .
docker run --env POLYGON_API_KEY=YOUR_KEY trading-platform --symbols AAPL,MSFT
```

`run_pipeline.sh` wraps `python -m trading_platform.run_daily` so you can pass any of its arguments.

### docker-compose

Start the web interface and scheduler together using the provided compose file:

```bash
docker compose build
docker compose up -d
```

Both services load variables from `.env` and share the `data/` and `reports/` directories.

### Scheduler Service

The scheduler runs `run_daily` automatically once per day. Launch it directly:

```bash
python -m trading_platform.scheduler
```

Use the web interface to start or stop the scheduler at any time.

## Planning Documents

Design notes are tracked in `design/plans/` using sequential IDs (e.g. `P001.md`).
Older date-based notes are summarized in `planning/archive.md`. See
[`design/PLAN_INDEX.md`](design/PLAN_INDEX.md) for a list of all planning files.

