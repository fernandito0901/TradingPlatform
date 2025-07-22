import os
import time
import sqlite3
import datetime
import json
import requests
import websocket

API_KEY = os.getenv("POLYGON_API_KEY", "2YpDJoJw1g_6pUS_xZzu2NBDm5szHJ5Q")
DB_FILE = 'market_data.db'
RATE_LIMIT_SEC = 1  # simple rate limit between requests
CACHE_QUOTE_MS = 5 * 1000
WS_URL = "wss://delayed.polygon.io/stocks"


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
    if resp.status_code == 403:
        # Let caller handle authorization failures explicitly
        raise requests.HTTPError("Forbidden", response=resp)
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
    # Starter plans cannot access the `/v2/last/trade` endpoint. Use the
    # snapshot endpoint instead which provides a recent price.
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
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO realtime_quotes VALUES (?,?,?)",
        (symbol, ts, price),
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
    params = {"apiKey": API_KEY, "greeks": "true"}
    data = rate_limited_get(url, params)
    options = data.get("results", [])
    for opt in options:
        details = opt.get("details", {})
        greeks = opt.get("greeks", {})
        ticker = details.get("ticker")
        c.execute(
            "INSERT OR REPLACE INTO option_chain VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                symbol,
                ticker,
                details.get("expiration_date"),
                details.get("strike_price"),
                details.get("contract_type"),
                None,
                None,
                opt.get("implied_volatility"),
                greeks.get("delta"),
                opt.get("day", {}).get("volume"),
                opt.get("open_interest"),
            ),
        )
    conn.commit()


def stream_quotes(symbol="AAPL"):
    """Stream real-time trades and quotes via Polygon's WebSocket."""

    def on_open(ws):
        auth = json.dumps({"action": "auth", "params": API_KEY})
        ws.send(auth)
        subs = json.dumps({"action": "subscribe", "params": f"T.{symbol},Q.{symbol}"})
        ws.send(subs)

    def on_message(ws, message):
        print(message)

    def on_error(ws, error):
        print("WebSocket error:", error)

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed", close_status_code, close_msg)

    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    print(f"Streaming live data for {symbol}... press Ctrl+C to stop")
    ws.run_forever()


def main(symbol="AAPL", stream=False):
    conn = init_db()
    fetch_ohlcv(conn, symbol)
    fetch_realtime_quote(conn, symbol)
    fetch_option_chain(conn, symbol)
    print("Data collection completed")
    if stream:
        stream_quotes(symbol)


if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    stream = len(sys.argv) > 2 and sys.argv[2] == "stream"
    main(sym, stream)
