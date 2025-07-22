import os
import time
import sqlite3
import datetime
import json

try:
    import requests
except ImportError as e:
    raise SystemExit(
        "Missing dependency 'requests'. Install it with 'python3 -m pip install requests'"
    ) from e

try:
    import websocket
except ImportError as e:
    raise SystemExit(
        "Missing dependency 'websocket-client'. Install it with 'python3 -m pip install websocket-client'"
    ) from e

API_KEY = os.getenv("POLYGON_API_KEY")
if not API_KEY:
    raise SystemExit(
        "Environment variable POLYGON_API_KEY is required.\n"
        "Sign up at https://polygon.io to obtain an API key."
    )
DB_FILE = "market_data.db"
RATE_LIMIT_SEC = 1  # simple rate limit between requests
CACHE_QUOTE_MS = 5 * 1000
WS_URL = "wss://delayed.polygon.io/stocks"
REALTIME_WS_URL = "wss://socket.polygon.io/stocks"


def init_db():
    """Initialize the SQLite database and return a connection.

    Returns
    -------
    sqlite3.Connection
        Open connection to ``DB_FILE`` with required tables created.
    """
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
        """CREATE TABLE IF NOT EXISTS minute_bars (
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
        """CREATE TABLE IF NOT EXISTS fundamentals (
            symbol TEXT,
            fetched_at INTEGER,
            data TEXT,
            PRIMARY KEY(symbol, fetched_at)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS corporate_actions (
            symbol TEXT,
            execution_date TEXT,
            action TEXT,
            details TEXT,
            PRIMARY KEY(symbol, execution_date, action)
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS indicators (
            symbol TEXT,
            t INTEGER,
            name TEXT,
            value REAL,
            PRIMARY KEY(symbol, t, name)
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
    """Fetch and cache 60 days of daily bars for a symbol."""

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


def fetch_minute_bars(conn, symbol):
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


def fetch_fundamentals(conn, symbol):
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


def fetch_corporate_actions(conn, symbol):
    """Fetch recent split events for the symbol."""
    url = "https://api.polygon.io/v3/reference/splits"
    params = {"ticker": symbol, "apiKey": API_KEY, "limit": 10}
    data = rate_limited_get(url, params)
    for act in data.get("results", []):
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO corporate_actions VALUES (?,?,?,?)",
            (
                symbol,
                act.get("execution_date"),
                "split",
                json.dumps(act),
            ),
        )
    conn.commit()


def fetch_indicator_sma(conn, symbol):
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
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO indicators VALUES (?,?,?,?)",
            (symbol, val.get("timestamp"), "sma50", val.get("value")),
        )
    conn.commit()


def stream_quotes(symbols="AAPL", realtime=False):
    """Stream trades and quotes via Polygon's WebSocket.

    Parameters
    ----------
    symbols : str
        Comma separated list of tickers to subscribe to.
    realtime : bool
        Use the real-time feed when True, otherwise use the delayed feed.
    """

    def on_open(ws):
        # Authenticate first. The subscription request will be sent
        # once we receive an auth_success message in on_message.
        auth = json.dumps({"action": "auth", "params": API_KEY})
        ws.send(auth)

    def subscribe(ws):
        chans = []
        for sym in symbols.split(","):
            chans.append(f"T.{sym}")
            chans.append(f"Q.{sym}")
        subs = json.dumps({"action": "subscribe", "params": ",".join(chans)})
        ws.send(subs)

    def on_message(ws, message):
        print(message)
        try:
            events = json.loads(message)
        except json.JSONDecodeError:
            return

        # Wait for authentication before subscribing to channels.
        for evt in events:
            if evt.get("status") == "auth_success":
                subscribe(ws)
            elif (
                evt.get("status") == "error" and evt.get("message") == "not authorized"
            ):
                # Fall back to delayed feed when real-time subscription fails
                if realtime:
                    print("Real-time feed unauthorized, switching to delayed feed...")
                    ws.close()
                    stream_quotes(symbols, realtime=False)
                else:
                    print("Subscription unauthorized; check your plan permissions")

    def on_error(ws, error):
        print("WebSocket error:", error)

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed", close_status_code, close_msg)

    url = REALTIME_WS_URL if realtime else WS_URL
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    print(
        f"Streaming {'real-time' if realtime else 'delayed'} data for {symbols}... press Ctrl+C to stop"
    )
    ws.run_forever()


def main(symbols="AAPL", stream=False, realtime=False):
    conn = init_db()
    for sym in symbols.split(","):
        fetch_ohlcv(conn, sym)
        fetch_minute_bars(conn, sym)
        fetch_realtime_quote(conn, sym)
        fetch_option_chain(conn, sym)
        fetch_fundamentals(conn, sym)
        fetch_corporate_actions(conn, sym)
        fetch_indicator_sma(conn, sym)
    print("Data collection completed")
    if stream:
        stream_quotes(symbols, realtime=realtime)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    sym = args[0] if args else "AAPL"
    stream = "stream" in args
    realtime = "realtime" in args
    main(sym, stream, realtime)
