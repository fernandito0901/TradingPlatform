"""Position evaluator engine for monitoring open trades."""

from __future__ import annotations

import argparse
import logging
import time

from .collector import api, db
from .collector.alerts import notify_position
from .portfolio import (
    PNL_FILE,
    PORTFOLIO_FILE,
    close_position,
    load_portfolio,
)
from .secret_filter import SecretFilter

try:  # optional when running without webapp
    from .webapp import socketio
except Exception:  # pragma: no cover - webapp not running
    socketio = None


DEFAULT_INTERVAL = 60
DEFAULT_STOP_LOSS = 0.05
DEFAULT_TAKE_PROFIT = 0.10


def evaluate_positions(
    conn,
    portfolio_file: str = PORTFOLIO_FILE,
    pnl_file: str = PNL_FILE,
    stop_loss: float = DEFAULT_STOP_LOSS,
    take_profit: float = DEFAULT_TAKE_PROFIT,
) -> None:
    """Evaluate open positions and close those hitting thresholds."""
    df = load_portfolio(portfolio_file)
    if df.empty:
        logging.info("No open positions to evaluate")
        return

    cur = conn.cursor()
    for _, row in df.iterrows():
        symbol = row["symbol"]
        avg_price = float(row["avg_price"])
        api.fetch_realtime_quote(conn, symbol)
        cur.execute(
            "SELECT price FROM realtime_quotes WHERE symbol=? ORDER BY t DESC LIMIT 1",
            (symbol,),
        )
        fetched = cur.fetchone()
        if not fetched:
            continue
        price = float(fetched[0])
        change = (price - avg_price) / avg_price
        if change <= -stop_loss or change >= take_profit:
            close_position(symbol, price, portfolio_file, pnl_file)
            notify_position(symbol, "Exit", price)
            logging.info("Closed %s at %.2f (%.2f%%)", symbol, price, change * 100)


def evaluate_loop(
    conn,
    portfolio_file: str = PORTFOLIO_FILE,
    pnl_file: str = PNL_FILE,
    interval: int = DEFAULT_INTERVAL,
    iterations: int = 0,
) -> None:
    """Run :func:`evaluate_positions` continuously."""
    count = 0
    while True:
        evaluate_positions(conn, portfolio_file, pnl_file)
        if socketio is not None:
            from .portfolio import load_pnl

            df = load_pnl(pnl_file)
            socketio.emit("pnl_update", df.to_dict(orient="records"))
        count += 1
        if iterations and count >= iterations:
            break
        time.sleep(interval)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point running the evaluator loop."""
    parser = argparse.ArgumentParser(description="Run position evaluator")
    parser.add_argument("--portfolio-file", default=PORTFOLIO_FILE)
    parser.add_argument("--pnl-file", default=PNL_FILE)
    parser.add_argument("--db-file", default="market_data.db")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    parser.add_argument("--iterations", type=int, default=0)
    parser.add_argument("--stop-loss", type=float, default=DEFAULT_STOP_LOSS)
    parser.add_argument("--take-profit", type=float, default=DEFAULT_TAKE_PROFIT)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log_level)
    logging.getLogger().addFilter(SecretFilter())
    conn = db.init_db(args.db_file)
    try:
        evaluate_loop(
            conn,
            portfolio_file=args.portfolio_file,
            pnl_file=args.pnl_file,
            interval=args.interval,
            iterations=args.iterations,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
