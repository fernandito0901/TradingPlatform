import os
import time
import sqlite3
import datetime
import requests

API_KEY = os.getenv('POLYGON_API_KEY', '2YpDJoJw1g_6pUS_xZzu2NBDm5szHJ5Q')
DB_FILE = 'market_data.db'
RATE_LIMIT_SEC = 1  # simple rate limit between requests
CACHE_QUOTE_MS = 5 * 1000


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS ohlcv (
            symbol TEXT,
            t INTEGER,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            PRIMARY KEY(symbol, t)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS realtime_quotes (
            symbol TEXT,
            t INTEGER PRIMARY KEY,
            price REAL
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS option_chain (
            symbol TEXT,
            contract TEXT,
            expiration DATE,
            strike REAL,
            option_type TEXT,
            bid REAL,
            ask REAL,
            iv REAL,
            delta REAL,
            volume REAL,
            open_interest REAL,
            PRIMARY KEY(symbol, contract)
        )"""
    )
    conn.commit()
    return conn


def rate_limited_get(url, params=None):
    time.sleep(RATE_LIMIT_SEC)
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_ohlcv(conn, symbol):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=60)
    start_ts = int(datetime.datetime.combine(start, datetime.time.min).timestamp() * 1000)
    end_ts = int(datetime.datetime.combine(end, datetime.time.min).timestamp() * 1000)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM ohlcv WHERE symbol=? AND t BETWEEN ? AND ?",
        (symbol, start_ts, end_ts),
    )
    if c.fetchone()[0] == (end - start).days + 1:
        return  # data already cached
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "apiKey": API_KEY}
    data = rate_limited_get(url, params)
    c = conn.cursor()
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


def fetch_realtime_quote(conn, symbol):
    c = conn.cursor()
    c.execute(
        "SELECT t FROM realtime_quotes WHERE symbol=? ORDER BY t DESC LIMIT 1",
        (symbol,),
    )
    row = c.fetchone()
    if row and int(time.time() * 1000) - row[0] < CACHE_QUOTE_MS:
        return
    url = f"https://api.polygon.io/v2/last/trade/{symbol}"
    params = {"apiKey": API_KEY}
    data = rate_limited_get(url, params)
    trade = data.get("results", data.get("last", {}))
    if not trade:
        return
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO realtime_quotes VALUES (?,?,?)",
        (symbol, trade.get("t", trade.get("timestamp")), trade.get("p", trade.get("price"))),
    )
    conn.commit()


def fetch_option_chain(conn, symbol):
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute(
        "SELECT COUNT(*) FROM option_chain WHERE symbol=? AND expiration>=?",
        (symbol, today),
    )
    if c.fetchone()[0]:
        return
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}"
    params = {"apiKey": API_KEY}
    data = rate_limited_get(url, params)
    options = data.get("results", {}).get("options", [])
    for opt in options:
        details = opt.get("details", {})
        greeks = opt.get("greeks", {})
        ticker = opt.get("ticker")
        c.execute(
            "INSERT OR REPLACE INTO option_chain VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                symbol,
                ticker,
                details.get("expiration_date"),
                details.get("strike_price"),
                details.get("type"),
                opt.get("bid"),
                opt.get("ask"),
                greeks.get("iv"),
                greeks.get("delta"),
                opt.get("volume"),
                opt.get("open_interest"),
            ),
        )
    conn.commit()


def main(symbol="AAPL"):
    conn = init_db()
    fetch_ohlcv(conn, symbol)
    fetch_realtime_quote(conn, symbol)
    fetch_option_chain(conn, symbol)
    print("Data collection completed")


if __name__ == "__main__":
    main()
