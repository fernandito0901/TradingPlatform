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

The REST API calls include:

- `/v2/aggs/ticker/{symbol}/prev` – previous close (delayed)
- `/v1/open-close/{symbol}/{date}` – daily open and close (delayed)
- `/v3/trades/{symbol}?limit=50` – recent trades (delayed)
- `/v3/quotes/{symbol}?limit=50` – recent quotes (delayed)
- `/v3/reference/options/contracts?underlying_ticker={symbol}` – option contracts
- `/v2/snapshot/locale/us/markets/stocks/tickers` – stock snapshot

## Reports

Model training metrics are written to `reports/dashboard.html`. Open this file
in a browser to view recent AUC scores. Pass ``cv=True`` to
``models.train`` to compute a 5-fold average AUC that appears as **CV AUC**.
The trainer automatically uses all feature columns (except ``t`` and
``target``), so new features are picked up without code changes.
The trainer automatically uses all feature columns (except ``t`` and
``target``), so new features are picked up without code changes.
Call ``generate_feature_dashboard`` with the features CSV to produce
`reports/feature_dashboard.html` for interactive exploration of feature
distributions. Historical results are stored in `reports/scoreboard.csv`.
Use ``generate_strategy_dashboard`` to write `reports/strategies.html` summarizing POP for available trades.
Risk metrics can be computed from `reports/scoreboard.csv` using the risk report CLI:

```bash
risk-report --scoreboard reports/scoreboard.csv --out-file reports/scoreboard_risk.csv
```
The `MAX_RISK` environment variable specifies per-strategy risk limits applied during simulations and evaluation.

Risk metrics can be computed from `reports/scoreboard.csv` using the risk report CLI:

```bash
risk-report --scoreboard reports/scoreboard.csv --out-file reports/scoreboard_risk.csv
```
The `MAX_RISK` environment variable specifies per-strategy risk limits applied during simulations and evaluation.


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
a Slack alert if ``SLACK_WEBHOOK_URL`` is configured. The completion message
includes a table of the day’s top trades with probability, momentum and other
factors so you can quickly review the rationale behind each recommendation.
The playbook generator automatically pads any missing model features with zeros
so LightGBM predictions run smoothly even if some columns are absent.
The feature pipeline requires at least sixty days of historical bars; if too few
rows are available ``models.train`` raises ``ValueError`` and the pipeline
aborts.
When the run completes, the top trades are printed to the console in the same
table format for local review.
a Slack alert if ``SLACK_WEBHOOK_URL`` is configured. The completion message
includes a table of the day’s top trades with probability, momentum and other
factors so you can quickly review the rationale behind each recommendation.
The playbook generator automatically pads any missing model features with zeros
so LightGBM predictions run smoothly even if some columns are absent.
The feature pipeline requires at least sixty days of historical bars; if too few
rows are available ``models.train`` raises ``ValueError`` and the pipeline
aborts.
When the run completes, the top trades are printed to the console in the same
table format for local review.

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

You can also backtest the latest features and model with:

```bash
backtest features/2025-01-01/features.csv models/model_20250101_1200.txt
```

You can also backtest the latest features and model with:

```bash
backtest features/2025-01-01/features.csv models/model_20250101_1200.txt
```

The CSV at `reports/scoreboard.csv` tracks daily AUC and optional PnL values.
Simulated trades are also logged in `reports/portfolio.csv` and realized
profits appended to `reports/pnl.csv`.

### Makefile Shortcuts

Common tasks are wrapped with Make targets:

```bash
make train ARGS="features.csv"
make tune ARGS="features.csv --symbol AAPL"
make backtest
make daily ARGS="--symbols AAPL"
```

`make backtest` runs `scripts/run_backtest.py`, which loads the latest features
and model to update `reports/pnl.csv`.

The web dashboard periodically fetches `/api/scoreboard` and `/api/pnl` so
`reports/scoreboard.csv` and `reports/pnl.csv` stay up to date without manual
uploads.

### Makefile Shortcuts

Common tasks are wrapped with Make targets:

```bash
make train ARGS="features.csv"
make tune ARGS="features.csv --symbol AAPL"
make backtest
make daily ARGS="--symbols AAPL"
```

`make backtest` runs `scripts/run_backtest.py`, which loads the latest features
and model to update `reports/pnl.csv`.

The web dashboard periodically fetches `/api/scoreboard` and `/api/pnl` so
`reports/scoreboard.csv` and `reports/pnl.csv` stay up to date without manual
uploads.

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
### Real-time Monitoring

Stream quotes for open positions and evaluate them continuously:

```bash
portfolio-stream --db-file market_data.db --portfolio-file reports/portfolio.csv
evaluator --portfolio-file reports/portfolio.csv --pnl-file reports/pnl.csv
```
`portfolio-stream` records real-time quotes in the database. The `evaluator` closes positions when stop-loss or take-profit thresholds are reached and appends PnL to `reports/pnl.csv`. Set `SLACK_WEBHOOK_URL` to receive alerts for entry and exit events.

### Real-time Monitoring

Stream quotes for open positions and evaluate them continuously:

```bash
portfolio-stream --db-file market_data.db --portfolio-file reports/portfolio.csv
evaluator --portfolio-file reports/portfolio.csv --pnl-file reports/pnl.csv
```
`portfolio-stream` records real-time quotes in the database. The `evaluator` closes positions when stop-loss or take-profit thresholds are reached and appends PnL to `reports/pnl.csv`. Set `SLACK_WEBHOOK_URL` to receive alerts for entry and exit events.


### Web Interface

Launch a local web UI for running commands:

```bash
webapp
```

The server binds to `0.0.0.0:5000` by default so it can be reached from outside the container. Customize the address with `WEBAPP_HOST` and `WEBAPP_PORT`. The entrypoint enables Flask's built-in server with ``allow_unsafe_werkzeug=True`` so the dashboard works when launched under Docker.

On first launch, the page prompts for API keys and saves them to `.env`.
After setup you can run the daily pipeline or connectivity checks with
buttons on the homepage. The dashboard automatically loads the latest playbook,
news headlines and portfolio data. A real-time trade feed updates via WebSocket
 (the pipeline broadcasts each recommended trade to connected clients) while
 charts show feature importance, backtest results and the equity curve from
 `reports/pnl.csv`. The sidebar lists your watchlist symbols and a market
 overview panel displays the most recent close for each symbol. Toast notifications now deduplicate messages and include *Clear All* / *Mark All as Read* buttons. A dark mode toggle changes the page theme. Trade recommendations refresh live with progress bars for POP and metrics cards show the model version. Scheduler controls remain available and recent results from `reports/scoreboard.csv` are displayed in a table. See `docs/ui_overview.md` for a visual guide to the layout.

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

