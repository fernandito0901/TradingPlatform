"""Asynchronous collector API using aiohttp."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Optional
import datetime as dt

import aiohttp

from . import api

API_KEY = api.API_KEY
NEWS_API_KEY = api.NEWS_API_KEY
WS_URL = api.WS_URL
REALTIME_WS_URL = api.REALTIME_WS_URL
RATE_LIMIT_SEC = api.RATE_LIMIT_SEC
CACHE_TTL = api.CACHE_TTL

_HTTP_CACHE: dict[str, tuple[float, dict]] = {}


async def rate_limited_get(
    session: aiohttp.ClientSession, url: str, params: Optional[dict] = None
) -> dict:
    """Perform a GET request with caching and rate limiting."""
    key = url + json.dumps(params or {}, sort_keys=True)
    now = time.time()
    if CACHE_TTL > 0:
        cached = _HTTP_CACHE.get(key)
        if cached and now - cached[0] < CACHE_TTL:
            logging.debug("Cache hit for %s", key)
            return cached[1]

    await asyncio.sleep(RATE_LIMIT_SEC)
    logging.debug("GET %s params=%s", url, params)
    async with session.get(url, params=params) as resp:
        if resp.status == 403:
            raise aiohttp.ClientResponseError(
                resp.request_info, resp.history, status=resp.status
            )
        resp.raise_for_status()
        data = await resp.json()
    if CACHE_TTL > 0:
        _HTTP_CACHE[key] = (now, data)
    return data


async def fetch_ohlcv(session: aiohttp.ClientSession, conn, symbol: str) -> None:
    logging.info("Fetching OHLCV for %s", symbol)
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
    params = {"adjusted": "true", "apiKey": API_KEY}
    data = await rate_limited_get(session, url, params)
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


async def fetch_option_chain(session: aiohttp.ClientSession, conn, symbol: str) -> None:
    logging.info("Fetching option chain for %s", symbol)
    c = conn.cursor()
    today = dt.date.today().isoformat()
    c.execute(
        "SELECT COUNT(*) FROM option_chain WHERE symbol=? AND expiration>=?",
        (symbol, today),
    )
    if c.fetchone()[0] > 0:
        return
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}"
    params = {"apiKey": API_KEY, "greeks": "true"}
    data = await rate_limited_get(session, url, params)
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


async def fetch_news(
    session: aiohttp.ClientSession, conn, symbol: str, limit: int = 5
) -> None:
    logging.info("Fetching news for %s", symbol)
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "pageSize": limit,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY,
    }
    data = await rate_limited_get(session, url, params)
    articles = data.get("articles", [])
    c = conn.cursor()
    for art in articles:
        c.execute(
            "INSERT OR REPLACE INTO news VALUES (?,?,?,?,?)",
            (
                symbol,
                art.get("publishedAt"),
                art.get("title"),
                art.get("url"),
                art.get("source", {}).get("name"),
            ),
        )
    conn.commit()


async def fetch_all(conn, symbol: str) -> None:
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            fetch_ohlcv(session, conn, symbol),
            fetch_option_chain(session, conn, symbol),
            fetch_news(session, conn, symbol),
        )
