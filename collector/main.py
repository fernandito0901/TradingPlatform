from . import api, db, stream


def main(symbols="AAPL", stream_data=False, realtime=False, db_file="market_data.db"):
    """Run all data collection tasks and optionally start streaming."""
    conn = db.init_db(db_file)
    for sym in symbols.split(","):
        api.fetch_ohlcv(conn, sym)
        api.fetch_minute_bars(conn, sym)
        api.fetch_realtime_quote(conn, sym)
        api.fetch_option_chain(conn, sym)
        api.fetch_fundamentals(conn, sym)
        api.fetch_corporate_actions(conn, sym)
        api.fetch_indicator_sma(conn, sym)
    print("Data collection completed")
    if stream_data:
        stream.stream_quotes(symbols, realtime=realtime)
