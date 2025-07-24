import logging

from ..config import Config
from ..load_env import load_env
from . import api, db, stream
from .logging_utils import setup_logging


def main(
    config: Config,
    stream_data: bool = False,
    realtime: bool = False,
):
    """Run data collection tasks and optionally start streaming.

    Parameters
    ----------
    config : Config
        Shared configuration object.
    stream_data : bool, default False
        Start streaming after fetching data.
    realtime : bool, default False
        Use the real-time WebSocket feed.
    """
    load_env()
    setup_logging(config.log_file, config.log_level)
    conn = db.init_db(config.db_file)
    for sym in config.symbols.split(","):
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
        stream.stream_quotes(config.symbols, realtime=realtime)
