import sqlite3


def init_db(db_file: str) -> sqlite3.Connection:
    """Initialize SQLite database and return connection."""
    conn = sqlite3.connect(db_file)
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
