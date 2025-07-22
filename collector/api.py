import datetime
import json
import os
import time
from typing import Optional

import requests

API_KEY = os.getenv("POLYGON_API_KEY")
if not API_KEY:
    raise SystemExit("POLYGON_API_KEY environment variable not set")

WS_URL = "wss://delayed.polygon.io/stocks"
REALTIME_WS_URL = "wss://socket.polygon.io/stocks"
RATE_LIMIT_SEC = 1
CACHE_QUOTE_MS = 5 * 1000


def rate_limited_get(url: str, params: Optional[dict] = None) -> dict:
    """Perform a GET request respecting a simple rate limit."""
    time.sleep(RATE_LIMIT_SEC)
    resp = requests.get(url, params=params)
    if resp.status_code == 403:
        raise requests.HTTPError("Forbidden", response=resp)
    resp.raise_for_status()
    return resp.json()


def fetch_ohlcv(conn, symbol: str):
    """Fetch and cache the last 60 days of daily OHLCV data."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=60)
    start_ts = int(
        datetime.datetime.combine(start, datetime.time.min).timestamp() * 1000
    )
    end_ts = int(datetime.datetime.combine(end, datetime.time.min).timestamp() * 1000)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM ohlcv WHERE symbol=? AND t BETWEEN ? AND ?",
        (symbol, start_ts, end_ts),
    )
    if c.fetchone()[0] == (end - start).days + 1:
        return
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "apiKey": API_KEY}
    data = rate_limited_get(url, params)
    for bar in data.get("results", []):
        c.execute(
            "INSERT OR REPLACE INTO ohlcv VALUES (?,?,?,?,?,?,?)",
            (
                symbol,
                bar["t"],
                bar["o"],
                bar["h"],
                bar["l"],
                bar["c"],
                bar["v"],
            ),
        )
    conn.commit()


def fetch_minute_bars(conn, symbol: str):
    """Fetch the last trading day's minute aggregates."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=1)
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start}/{end}"
    params = {"adjusted": "true", "apiKey": API_KEY, "limit": 50000}
    data = rate_limited_get(url, params)
    c = conn.cursor()
    for bar in data.get("results", []):
        c.execute(
            "INSERT OR REPLACE INTO minute_bars VALUES (?,?,?,?,?,?,?)",
            (
                symbol,
                bar["t"],
                bar["o"],
                bar["h"],
                bar["l"],
                bar["c"],
                bar["v"],
            ),
        )
    conn.commit()


def fetch_realtime_quote(conn, symbol: str):
    """Fetch a recent trade price via the snapshot endpoint and cache it."""
    c = conn.cursor()
    c.execute(
        "SELECT t FROM realtime_quotes WHERE symbol=? ORDER BY t DESC LIMIT 1",
        (symbol,),
    )
    row = c.fetchone()
    if row and int(time.time() * 1000) - row[0] < CACHE_QUOTE_MS:
        return
    snap_url = "https://api.polygon.io/v3/snapshot"
    snap_params = {"ticker": symbol, "apiKey": API_KEY}
    data = rate_limited_get(snap_url, snap_params)
    results = data.get("results", [])
    if not results:
        return
    session = results[0].get("session", {})
    price = session.get("price")
    ts = session.get("last_updated")
    if not price:
        return
    c.execute(
        "INSERT OR REPLACE INTO realtime_quotes VALUES (?,?,?)",
        (symbol, ts, price),
    )
    conn.commit()


def fetch_option_chain(conn, symbol: str):
    """Fetch option snapshot data and store it in the database."""
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute(
        "SELECT COUNT(*) FROM option_chain WHERE symbol=? AND expiration>=?",
        (symbol, today),
    )
    if c.fetchone()[0] > 0:
        return
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}"
    params = {"apiKey": API_KEY, "greeks": "true"}
    data = rate_limited_get(url, params)
    options = data.get("results", [])
    for opt in options:
        details = opt.get("details", {})
        greeks = opt.get("greeks", {})
        last_quote = opt.get("last_quote", {})
        ticker = details.get("ticker")
        c.execute(
            "INSERT OR REPLACE INTO option_chain VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                symbol,
                ticker,
                details.get("expiration_date"),
                details.get("strike_price"),
                details.get("contract_type"),
                (
                    last_quote.get("bid", {}).get("p")
                    if isinstance(last_quote.get("bid"), dict)
                    else None
                ),
                (
                    last_quote.get("ask", {}).get("p")
                    if isinstance(last_quote.get("ask"), dict)
                    else None
                ),
                opt.get("implied_volatility"),
                greeks.get("delta"),
                opt.get("day", {}).get("volume"),
                opt.get("open_interest"),
            ),
        )
    conn.commit()


def fetch_fundamentals(conn, symbol: str):
    """Fetch fundamental data and store raw JSON."""
    url = "https://api.polygon.io/vX/reference/financials"
    params = {"ticker": symbol, "limit": 1, "apiKey": API_KEY}
    data = rate_limited_get(url, params)
    if not data.get("results"):
        return
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO fundamentals VALUES (?,?,?)",
        (symbol, int(time.time()), json.dumps(data["results"][0])),
    )
    conn.commit()


def fetch_corporate_actions(conn, symbol: str):
    """Fetch recent split events for the symbol."""
    url = "https://api.polygon.io/v3/reference/splits"
    params = {"ticker": symbol, "apiKey": API_KEY, "limit": 10}
    data = rate_limited_get(url, params)
    for act in data.get("results", []):
        conn.execute(
            "INSERT OR REPLACE INTO corporate_actions VALUES (?,?,?,?)",
            (
                symbol,
                act.get("execution_date"),
                "split",
                json.dumps(act),
            ),
        )
    conn.commit()


def fetch_indicator_sma(conn, symbol: str):
    """Fetch a 50 day simple moving average."""
    url = f"https://api.polygon.io/v1/indicators/sma/{symbol}"
    params = {
        "timespan": "day",
        "window": 50,
        "series_type": "close",
        "apiKey": API_KEY,
    }
    data = rate_limited_get(url, params)
    for val in data.get("results", {}).get("values", []):
        conn.execute(
            "INSERT OR REPLACE INTO indicators VALUES (?,?,?,?)",
            (symbol, val.get("timestamp"), "sma50", val.get("value")),
        )
    conn.commit()
