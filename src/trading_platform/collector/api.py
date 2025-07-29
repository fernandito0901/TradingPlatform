import datetime
import json
import logging
import os
import time
from typing import Optional

import requests
from requests import HTTPError

MARKET_STATUS_URL = "https://api.polygon.io/v1/marketstatus/now"

from .alerts import AlertAggregator

API_KEY = os.getenv("POLYGON_API_KEY")
if not API_KEY:
    raise RuntimeError("POLYGON_API_KEY not configured")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    raise RuntimeError("NEWS_API_KEY not configured")

WS_URL = "wss://delayed.polygon.io/stocks"
REALTIME_WS_URL = "wss://socket.polygon.io/stocks"
RATE_LIMIT_SEC = 1
CACHE_QUOTE_MS = 5 * 1000
CACHE_TTL = int(os.getenv("CACHE_TTL", "0"))

_HTTP_CACHE: dict[str, tuple[float, dict]] = {}


def market_open(asset: str = "stocks") -> bool:
    """Return ``True`` if the market for ``asset`` is open."""

    try:
        resp = requests.get(MARKET_STATUS_URL, params={"apiKey": API_KEY}, timeout=5)
        resp.raise_for_status()
        status = resp.json().get(asset, {})
        return status.get("market") == "open"
    except Exception as exc:  # network or parse error
        logging.warning("market status check failed: %s", exc)
        return True


class NoData(Exception):
    """Raised when an API endpoint returns no results."""


def rate_limited_get(url: str, params: Optional[dict] = None) -> dict:
    """Perform a GET request with caching and rate limiting."""
    key = url + json.dumps(params or {}, sort_keys=True)
    now = time.time()
    if CACHE_TTL > 0:
        cached = _HTTP_CACHE.get(key)
        if cached and now - cached[0] < CACHE_TTL:
            logging.debug("Cache hit for %s", key)
            return cached[1]

    for attempt in range(3):
        time.sleep(RATE_LIMIT_SEC)
        logging.debug("GET %s params=%s", url, params)
        resp = requests.get(url, params=params)
        if resp.status_code == 403:
            if not market_open():
                logging.warning("Market closed—skipping request %s", url)
                return {}
            raise RuntimeError(
                "Polygon API key rejected – check POLYGON_API_KEY & plan."
            )
        if resp.status_code == 429:
            if attempt < 2:
                time.sleep(2**attempt)
                continue
        resp.raise_for_status()
        data = resp.json()
        if CACHE_TTL > 0:
            _HTTP_CACHE[key] = (now, data)
        return data

    resp.raise_for_status()
    return resp.json()


def fetch_prev_close(symbol: str) -> dict:
    """Return the previous day's close data."""

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
    params = {"apiKey": API_KEY}
    return rate_limited_get(url, params)


def fetch_open_close(symbol: str, date: str) -> dict:
    """Return OHLC data for ``date`` using the aggregates endpoint.

    Raises
    ------
    NoData
        If the API returns no results for the given symbol and date.
    """

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{date}/{date}"
    params = {"adjusted": "true", "apiKey": API_KEY}
    try:
        data = rate_limited_get(url, params)
    except HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            raise NoData(symbol) from exc
        raise
    results = data.get("results", [])
    if not results:
        raise NoData(symbol)
    return results[0]


def fetch_trades(symbol: str, limit: int = 50) -> dict:
    """Return the latest ``limit`` trades."""

    url = f"https://api.polygon.io/v3/trades/{symbol}"
    params = {"limit": limit, "apiKey": API_KEY}
    return rate_limited_get(url, params)


def fetch_quotes(symbol: str, limit: int = 50) -> dict:
    """Return the latest ``limit`` quotes."""

    url = f"https://api.polygon.io/v3/quotes/{symbol}"
    params = {"limit": limit, "apiKey": API_KEY}
    return rate_limited_get(url, params)


def fetch_snapshot_tickers() -> dict:
    """Return snapshot data for US stock tickers."""

    url = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers"
    params = {"apiKey": API_KEY}
    return rate_limited_get(url, params)


def fetch_ohlcv(conn, symbol: str):
    """Fetch daily OHLCV data incrementally for the last 60 days."""
    logging.info("Fetching OHLCV for %s", symbol)
    end = datetime.date.today()
    c = conn.cursor()
    c.execute("SELECT MAX(t) FROM ohlcv WHERE symbol=?", (symbol,))
    row = c.fetchone()
    if row[0]:
        last_ts = row[0] // 1000
        start = datetime.date.fromtimestamp(last_ts) + datetime.timedelta(days=1)
    else:
        start = end - datetime.timedelta(days=60)
    if start > end:
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
    logging.info("Fetching minute bars for %s", symbol)
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
    logging.info("Fetching snapshot quote for %s", symbol)
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
    logging.info("Fetching option chain for %s", symbol)
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
    logging.info("Fetching fundamentals for %s", symbol)
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
    logging.info("Fetching corporate actions for %s", symbol)
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
    logging.info("Fetching SMA indicator for %s", symbol)
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


def fetch_news(
    conn,
    symbol: str,
    limit: int = 5,
    aggregator: AlertAggregator | None = None,
) -> None:
    """Fetch latest news articles for the given symbol.

    Parameters
    ----------
    conn : sqlite3.Connection
        Database connection.
    symbol : str
        Ticker symbol to fetch headlines for.
    limit : int, default 5
        Maximum number of articles to fetch.
    aggregator : AlertAggregator, optional
        Alert aggregator that receives headlines for Slack notifications.
    """
    logging.info("Fetching news for %s", symbol)
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "pageSize": limit,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY,
    }
    data = rate_limited_get(url, params)
    articles = data.get("articles", [])
    c = conn.cursor()
    for art in articles:
        c.execute(
            "INSERT INTO news(symbol, title, url, published_at) VALUES (?,?,?,?)",
            (
                symbol,
                art.get("title"),
                art.get("url"),
                art.get("publishedAt"),
            ),
        )
        if aggregator:
            aggregator.add_news(art.get("title", ""), art.get("url", ""))
    conn.commit()
