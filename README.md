# Market Data Collector

This script polls the [Polygon](https://polygon.io) REST API to collect
historical bars, real‑time quotes and option chain snapshots for a given
symbol. Data is cached in a local SQLite database to avoid redundant API
calls and to persist data between runs.

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

The script fetches the last 60 days of OHLCV data, a recent quote from the
snapshot endpoint, and the weekly option chain for the default symbol `AAPL`.
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
