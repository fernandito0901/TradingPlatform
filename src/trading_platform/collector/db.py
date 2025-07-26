import sqlite3
from pathlib import Path
from trading_platform.reports import REPORTS_DIR


def init_db(db_file: str) -> sqlite3.Connection:
    """Initialize SQLite database and return connection.

    Tables
    ------
    - ``ohlcv`` (symbol, t, open, high, low, close, volume)
    - ``minute_bars`` (symbol, t, open, high, low, close, volume)
    - ``fundamentals`` (symbol, fetched_at, data)
    - ``corporate_actions`` (symbol, execution_date, action, details)
    - ``indicators`` (symbol, t, name, value)
    - ``realtime_quotes`` (symbol, t, price)
    - ``option_chain`` (symbol, contract, expiration, strike, option_type,
      bid, ask, iv, delta, volume, open_interest)
    - ``news`` (symbol, published_at, title, url, source)
    """
    if db_file == ":memory:" or db_file.startswith("file::memory"):
        conn = sqlite3.connect(db_file, uri=db_file.startswith("file:"))
    else:
        path = Path(db_file)
        if not path.is_absolute():
            path = REPORTS_DIR / path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path)
        except sqlite3.OperationalError:
            path.touch()
            conn = sqlite3.connect(path)

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
    c.execute(
        """CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            title TEXT,
            url TEXT,
            published_at DATETIME
        )"""
    )
    conn.commit()
    return conn
