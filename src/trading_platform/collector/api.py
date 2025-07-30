import json
import logging
import os
import time
import datetime as dt
from datetime import datetime
import pandas_market_calendars as mcal
from typing import Optional
import zoneinfo

import requests
from requests import HTTPError

MARKET_STATUS_URL = "https://api.polygon.io/v1/marketstatus/now"

from .alerts import AlertAggregator


def _get_polygon_key() -> str:
    """Return Polygon API key or raise if missing."""
    key = os.getenv("POLYGON_API_KEY")
    if not key:
        raise RuntimeError("POLYGON_API_KEY not configured")
    return key


def _get_news_key() -> str:
    """Return News API key or raise if missing."""
    key = os.getenv("NEWS_API_KEY")
    if not key:
        raise RuntimeError("NEWS_API_KEY not configured")
    return key


WS_URL = "wss://delayed.polygon.io/stocks"
REALTIME_WS_URL = "wss://socket.polygon.io/stocks"
RATE_LIMIT_SEC = 1
CACHE_QUOTE_MS = 5 * 1000
CACHE_TTL = int(os.getenv("CACHE_TTL", "0"))

_HTTP_CACHE: dict[str, tuple[float, dict]] = {}

# US/Eastern timezone for session checks
EASTERN = zoneinfo.ZoneInfo("America/New_York")


nyse = mcal.get_calendar("NYSE")


def is_equity_session(now: datetime | None = None) -> bool:
    """Return ``True`` if equities are trading now based on NYSE calendar."""

    if os.getenv("TESTING"):
        return True
    now = now or datetime.now(EASTERN)
    schedule = nyse.schedule(start_date=now.date(), end_date=now.date())
    if schedule.empty:
        return False
    open_t = schedule.iloc[0]["market_open"].tz_convert(EASTERN)
    close_t = schedule.iloc[0]["market_close"].tz_convert(EASTERN)
    return open_t <= now <= close_t


def is_options_session(now: datetime | None = None) -> bool:
    """Return ``True`` if options are trading now using NYSE calendar."""

    if os.getenv("TESTING"):
        return True
    now = now or datetime.now(EASTERN)
    schedule = nyse.schedule(start_date=now.date(), end_date=now.date())
    if schedule.empty:
        return False
    open_t = (
        schedule.iloc[0]["market_open"].tz_convert(EASTERN).replace(hour=9, minute=30)
    )
    close_t = (
        schedule.iloc[0]["market_close"].tz_convert(EASTERN).replace(hour=16, minute=0)
    )
    return open_t <= now <= close_t


def is_market_open(asset: str = "stocks") -> bool:
    """Return ``True`` if the Polygon market for ``asset`` is open."""

    try:
        resp = requests.get(
            MARKET_STATUS_URL, params={"apiKey": _get_polygon_key()}, timeout=5
        )
        resp.raise_for_status()
        status = resp.json().get(asset, {})
        return status.get("market") == "open"
    except Exception as exc:  # network or parse error
        logging.warning("market status check failed: %s", exc)
        return True


class NoData(Exception):
    """Raised when an API endpoint returns no results."""


def rate_limited_get(
    url: str, params: Optional[dict] = None, max_retries: int = 3
) -> dict:
    """Perform a GET request with caching and rate limiting."""
    key = url + json.dumps(params or {}, sort_keys=True)
    now = time.time()
    if CACHE_TTL > 0:
        cached = _HTTP_CACHE.get(key)
        if cached and now - cached[0] < CACHE_TTL:
            logging.debug("Cache hit for %s", key)
            return cached[1]

    for attempt in range(max_retries):
        time.sleep(RATE_LIMIT_SEC)
        logging.debug("GET %s params=%s", url, params)
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 403:
            text = resp.text.lower()
            if "market" in text:
                logging.info("Polygon: market closed – skipping")
                return None
            if b"market is closed" in resp.content.lower() or not is_market_open():
                logging.warning(
                    "Polygon 403 – probably closed market; retry after 15 min"
                )
                time.sleep(900)
                continue
            raise RuntimeError(
                "Polygon API key rejected – check POLYGON_API_KEY & plan."
            )
        if resp.status_code == 429:
            if attempt < max_retries - 1:
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

    if not is_equity_session():
        logging.info("Market closed – skipping fetch_prev_close for %s", symbol)
        return {}

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
    params = {"apiKey": _get_polygon_key()}
    return rate_limited_get(url, params)


def fetch_open_close(symbol: str, date: str) -> dict:
    """Return OHLC data for ``date`` using the aggregates endpoint.

    Raises
    ------
    NoData
        If the API returns no results for the given symbol and date.
    """

    if not is_equity_session():
        logging.info("Market closed – skipping fetch_open_close for %s", symbol)
        return {}

    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{date}/{date}"
    params = {"adjusted": "true", "apiKey": _get_polygon_key()}
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

    if not is_equity_session():
        logging.info("Market closed – skipping fetch_trades for %s", symbol)
        return {}

    url = f"https://api.polygon.io/v3/trades/{symbol}"
    params = {"limit": limit, "apiKey": _get_polygon_key()}
    return rate_limited_get(url, params)


def fetch_quotes(symbol: str, limit: int = 50) -> dict:
    """Return the latest ``limit`` quotes."""

    if not is_equity_session():
        logging.info("Market closed – skipping fetch_quotes for %s", symbol)
        return {}

    url = f"https://api.polygon.io/v3/quotes/{symbol}"
    params = {"limit": limit, "apiKey": _get_polygon_key()}
    return rate_limited_get(url, params)


def fetch_snapshot_tickers() -> dict:
    """Return snapshot data for US stock tickers."""

    if not is_equity_session():
        logging.info("Market closed – skipping fetch_snapshot_tickers")
        return {}

    url = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers"
    params = {"apiKey": _get_polygon_key()}
    return rate_limited_get(url, params)


def fetch_ohlcv(conn, symbol: str):
    """Fetch daily OHLCV data incrementally for the last 60 days."""
    logging.info("Fetching OHLCV for %s", symbol)
    if not is_equity_session():
        logging.info("Market closed – skipping fetch_ohlcv for %s", symbol)
        return
    end = dt.date.today()
    c = conn.cursor()
    c.execute("SELECT MAX(t) FROM ohlcv WHERE symbol=?", (symbol,))
    row = c.fetchone()
    if row[0]:
        last_ts = row[0] // 1000
        start = dt.date.fromtimestamp(last_ts) + dt.timedelta(days=1)
    else:
        start = end - dt.timedelta(days=60)
    if start > end:
        return
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "apiKey": _get_polygon_key()}
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
    if not is_equity_session():
        logging.info("Market closed – skipping fetch_minute_bars for %s", symbol)
        return
    end = dt.date.today()
    start = end - dt.timedelta(days=1)
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/minute/{start}/{end}"
    params = {"adjusted": "true", "apiKey": _get_polygon_key(), "limit": 50000}
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
    if not is_equity_session():
        logging.info("Market closed – skipping fetch_realtime_quote for %s", symbol)
        return
    c = conn.cursor()
    c.execute(
        "SELECT t FROM realtime_quotes WHERE symbol=? ORDER BY t DESC LIMIT 1",
        (symbol,),
    )
    row = c.fetchone()
    if row and int(time.time() * 1000) - row[0] < CACHE_QUOTE_MS:
        return
    snap_url = "https://api.polygon.io/v3/snapshot"
    snap_params = {"ticker": symbol, "apiKey": _get_polygon_key()}
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
    if not is_options_session():
        logging.info(
            "Options market closed – skipping fetch_option_chain for %s", symbol
        )
        return
    c = conn.cursor()
    today = dt.date.today().isoformat()
    c.execute(
        "SELECT COUNT(*) FROM option_chain WHERE symbol=? AND expiration>=?",
        (symbol, today),
    )
    if c.fetchone()[0] > 0:
        return
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}"
    params = {"apiKey": _get_polygon_key(), "greeks": "true"}
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
    if not is_equity_session():
        logging.info("Market closed – skipping fetch_fundamentals for %s", symbol)
        return
    url = "https://api.polygon.io/vX/reference/financials"
    params = {"ticker": symbol, "limit": 1, "apiKey": _get_polygon_key()}
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
    if not is_equity_session():
        logging.info("Market closed – skipping fetch_corporate_actions for %s", symbol)
        return
    url = "https://api.polygon.io/v3/reference/splits"
    params = {"ticker": symbol, "apiKey": _get_polygon_key(), "limit": 10}
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
    if not is_equity_session():
        logging.info("Market closed – skipping fetch_indicator_sma for %s", symbol)
        return
    url = f"https://api.polygon.io/v1/indicators/sma/{symbol}"
    params = {
        "timespan": "day",
        "window": 50,
        "series_type": "close",
        "apiKey": _get_polygon_key(),
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
        "apiKey": _get_news_key(),
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
