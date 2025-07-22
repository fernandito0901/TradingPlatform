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

Install dependencies with:

```bash
pip install requests websocket-client
```

## Usage

Set your Polygon API key in the environment variable `POLYGON_API_KEY` or
edit `market_data_collector.py` to include your key. Then run:

```bash
python3 market_data_collector.py
```

The script fetches the last 60 days of OHLCV data, the most recent minute
aggregates, a delayed quote from the snapshot endpoint, and the weekly option
chain for the default symbol `AAPL`. Basic fundamentals, recent split history
and a 50‑day SMA are stored as well.
Adjust the symbol by running:

```bash
python3 market_data_collector.py TSLA
```

Collected data is stored in `market_data.db`.

To stream delayed trades and quotes continuously, pass the `stream` argument.
The script connects to Polygon's delayed WebSocket, which is available on the
Starter plan:

```bash
python3 market_data_collector.py AAPL stream
```

The WebSocket feed will print data to the console until interrupted.

## Starter Plan Compatibility

The collector uses endpoints that are accessible with Polygon's **Stocks** and
**Options** starter plans. Quotes and WebSocket data are delayed by 15 minutes,
and option snapshots may omit bid/ask data. Additional fundamentals,
corporate actions and technical indicators are fetched for future use when
available.
