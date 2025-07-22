import argparse


def parse_args(argv=None):
    """Parse command line arguments for the collector CLI."""
    parser = argparse.ArgumentParser(description="Market data collector")
    parser.add_argument(
        "symbols",
        nargs="?",
        default="AAPL",
        help="Comma separated list of ticker symbols",
    )
    parser.add_argument(
        "--db-file",
        default="market_data.db",
        help="Path to SQLite database file",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Start streaming after fetching data",
    )
    parser.add_argument(
        "--realtime",
        action="store_true",
        help="Use real-time WebSocket feed",
    )
    return parser.parse_args(argv)
