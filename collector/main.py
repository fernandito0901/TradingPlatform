import logging
from . import api, db, stream
from .logging_utils import setup_logging


def main(
    symbols="AAPL",
    stream_data=False,
    realtime=False,
    db_file="market_data.db",
    log_file=None,
    log_level="INFO",
):
    """Run data collection tasks and optionally start streaming.

    Parameters
    ----------
    symbols : str, default "AAPL"
        Comma-separated list of ticker symbols.
    stream_data : bool, default False
        Start streaming after fetching data.
    realtime : bool, default False
        Use the real-time WebSocket feed.
    db_file : str, default "market_data.db"
        SQLite database file path.
    log_file : str, optional
        File path to write logs. Defaults to stdout.
    log_level : str, default "INFO"
        Logging level.
    """
    setup_logging(log_file, log_level)
    conn = db.init_db(db_file)
    for sym in symbols.split(","):
        api.fetch_ohlcv(conn, sym)
        api.fetch_minute_bars(conn, sym)
        api.fetch_realtime_quote(conn, sym)
        api.fetch_option_chain(conn, sym)
        api.fetch_fundamentals(conn, sym)
        api.fetch_corporate_actions(conn, sym)
        api.fetch_indicator_sma(conn, sym)
        api.fetch_news(conn, sym)
    logging.info("Data collection completed")
    if stream_data:
        stream.stream_quotes(symbols, realtime=realtime)
