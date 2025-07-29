"""Daily pipeline orchestration."""

import asyncio
import json
import logging
from pathlib import Path

from features import run_pipeline
from trading_platform.models import train as train_model
from trading_platform.reports import REPORTS_DIR
from trading_platform.reports.dashboard import generate_dashboard
from trading_platform.reports.feature_dashboard import generate_feature_dashboard
from trading_platform.reports.scoreboard import update_scoreboard

from . import notifier
from .collector import api, api_async, db, verify
from .collector.alerts import AlertAggregator
from .config import Config, load_config
from .playbook.generate import generate_playbook

try:  # optional during CLI usage
    from .webapp import socketio
except Exception:  # pragma: no cover - webapp not running
    socketio = None


def run(config: Config) -> str:
    """Run full data pipeline and notify Slack on completion.

    Parameters
    ----------
    config : Config
        Runtime configuration produced by :func:`load_config`.

    Returns
    -------
    str
        Path to the generated playbook JSON file.
    """

    if not verify.verify(config.symbols):
        raise SystemExit("Connectivity check failed")

    conn = db.init_db(config.db_file)
    agg = AlertAggregator(config.slack_webhook_url)
    for sym in config.symbols.split(","):
        if config.use_async:
            asyncio.run(api_async.fetch_all(conn, sym, aggregator=agg))
        else:
            api.fetch_ohlcv(conn, sym)
            api.fetch_option_chain(conn, sym)
            api.fetch_news(conn, sym, aggregator=agg)

    try:
        feat_csv = run_pipeline(config, [config.symbols.split(",")[0]])
        res = train_model(feat_csv, "models", symbol=config.symbols.split(",")[0])
        if not res.model_path:
            raise RuntimeError("drift guard triggered")
        generate_dashboard(res.train_auc, res.test_auc, cv_auc=res.cv_auc)
        generate_feature_dashboard(feat_csv)
        pb_path = generate_playbook(feat_csv, res.model_path)
        update_scoreboard(
            pb_path,
            res.test_auc,
            model_path=res.model_path,
            train_auc=res.train_auc,
            test_auc=res.test_auc,
            cv_auc=res.cv_auc,
            window_days=res.window_days,
            holdout_auc=res.holdout_auc,
        )
        with open(pb_path) as f:
            pb = json.load(f)
        headers = [
            "Symbol",
            "Score",
            "ProbUp",
            "Mom",
            "News",
            "IV",
            "UOA",
            "Garch",
        ]
        print("Recommended trades:")
        print(" | ".join(headers))
        rows = []
        for trade in pb.get("trades", []):
            row = (
                str(trade.get("t", "")),
                f"{trade.get('score', 0.0):.2f}",
                f"{trade.get('prob_up', 0.0):.2f}",
                f"{trade.get('momentum', 0.0):.2f}",
                f"{trade.get('news_sent', 0.0):.2f}",
                f"{trade.get('iv_edge', 0.0):.2f}",
                f"{trade.get('uoa', 0.0):.2f}",
                f"{trade.get('garch_spike', 0.0):.2f}",
            )
            rows.append(" | ".join(row))
            print(rows[-1])
        slack_message = ["Recommended trades:", " | ".join(headers)] + rows
        notifier.send_slack("\n".join(slack_message))
        if socketio:
            for trade in pb.get("trades", []):
                socketio.emit("trade", trade)
    except Exception as exc:
        agg.flush()
        notifier.send_slack(f"Pipeline failed: {exc}")
        raise

    logging.info("Pipeline completed: %s", pb_path)
    demo_dir = Path(__file__).resolve().parent / "reports" / "demo"
    for name in ["pnl.csv", "trades.csv", "scoreboard.csv", "news.csv"]:
        dest = REPORTS_DIR / name
        if not dest.exists():
            src = demo_dir / name
            if src.exists():
                dest.write_text(src.read_text())
    agg.flush()
    notifier.send_slack(f"Pipeline completed: {pb_path}")
    if socketio:
        socketio.emit("dashboard-refresh", {})
    return pb_path


def run_intraday(config: Config) -> None:
    """Lightweight intraday refresh pipeline."""
    try:
        run(config)
    except Exception as exc:  # pragma: no cover - just log
        logging.error("intraday job failed: %s", exc)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the daily pipeline CLI."""
    config = load_config(argv)
    run(config)


if __name__ == "__main__":
    main()
