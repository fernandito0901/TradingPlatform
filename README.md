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

## Configuration

The collector relies on a couple of environment variables and optional
command‑line flags:

- **`POLYGON_API_KEY`**: API key required for all REST and WebSocket requests.
- **`CACHE_TTL`**: Time‑to‑live in seconds for HTTP response caching. Set to
  `0` to disable caching.

Logging can be directed to a file and the verbosity adjusted using the
`--log-file` and `--log-level` arguments, respectively.

## Usage

Export your `POLYGON_API_KEY` and set any optional variables described in the
[Configuration](#configuration) section. Then run the script with optional
arguments:

```bash
python3 market_data_collector.py --symbols AAPL,MSFT --stream --realtime --db-file mydata.db
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
python3 market_data_collector.py --symbols AAPL --stream
```

To stream multiple tickers, separate them with commas and optionally pass the
`realtime` flag to use the live feed instead of the delayed one:

```bash
python3 market_data_collector.py --symbols AAPL,MSFT --stream --realtime
```

The client waits for the connection to be authenticated before subscribing to trade and quote channels. If a `not authorized` error is returned when using the real-time feed, the collector automatically reconnects using the delayed WebSocket. The feed prints trade and quote data until interrupted.

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
in a browser to view recent AUC scores.
