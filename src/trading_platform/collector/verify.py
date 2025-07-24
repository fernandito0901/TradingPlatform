import argparse
import logging
import os

from ..load_env import load_env

from . import api, db


def verify(
    symbols: str = "AAPL", polygon_key: str | None = None, news_key: str | None = None
) -> bool:
    """Check API connectivity for a set of symbols.

    Parameters
    ----------
    symbols : str, default "AAPL"
        Comma-separated list of ticker symbols.
    polygon_key : str, optional
        Polygon API key. Overrides ``POLYGON_API_KEY`` environment variable.
    news_key : str, optional
        NewsAPI key. Overrides ``NEWS_API_KEY`` environment variable.

    Returns
    -------
    bool
        ``True`` if all requests succeed, ``False`` otherwise.
    """
    if polygon_key:
        os.environ["POLYGON_API_KEY"] = polygon_key
    if news_key:
        os.environ["NEWS_API_KEY"] = news_key

    conn = db.init_db(":memory:")
    try:
        for sym in symbols.split(",")[:5]:
            api.fetch_ohlcv(conn, sym)
            api.fetch_option_chain(conn, sym)
    except Exception as exc:  # pragma: no cover - debug log
        logging.error("Connectivity check failed: %s", exc)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the connectivity checker."""
    load_env()
    parser = argparse.ArgumentParser(description="Verify API keys and connectivity")
    parser.add_argument("--polygon-key", help="Polygon API key")
    parser.add_argument("--news-key", help="NewsAPI key")
    parser.add_argument(
        "--symbols", default="AAPL", help="Comma separated list of ticker symbols"
    )
    args = parser.parse_args(argv)
    success = verify(args.symbols, args.polygon_key, args.news_key)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
