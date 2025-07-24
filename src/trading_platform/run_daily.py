"""Daily pipeline orchestration."""

import argparse
import logging
from pathlib import Path

from .collector import api, db, verify
from .features import run_pipeline
from .models import train as train_model
from .playbook.generate import generate_playbook


def run(symbols: str = "AAPL", db_file: str = "market_data.db") -> str:
    """Run full data pipeline after a connectivity check."""
    if not verify.verify(symbols):
        raise SystemExit("Connectivity check failed")

    conn = db.init_db(db_file)
    for sym in symbols.split(","):
        api.fetch_ohlcv(conn, sym)
        api.fetch_option_chain(conn, sym)
        api.fetch_news(conn, sym)

    feat_csv = run_pipeline(conn, symbols.split(",")[0])
    model_path = str(Path(__file__).resolve().parent / "models" / "model.txt")
    train_model(feat_csv, model_path)
    pb_path = generate_playbook(feat_csv, model_path)
    logging.info("Pipeline completed: %s", pb_path)
    return pb_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run daily data pipeline")
    parser.add_argument("--symbols", default="AAPL")
    parser.add_argument("--db-file", default="market_data.db")
    args = parser.parse_args(argv)
    run(args.symbols, args.db_file)


if __name__ == "__main__":
    main()
