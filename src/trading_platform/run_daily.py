"""Daily pipeline orchestration."""

import asyncio
import logging
from pathlib import Path

from .config import Config, load_config

from .collector import api, api_async, db, verify
from .collector.alerts import AlertAggregator
from .features import run_pipeline
from .models import train as train_model
from .playbook.generate import generate_playbook
from . import notifier
from reports.dashboard import generate_dashboard
from reports.feature_dashboard import generate_feature_dashboard
from reports.scoreboard import update_scoreboard


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
        feat_csv = run_pipeline(conn, config.symbols.split(",")[0])
        model_path = str(Path(__file__).resolve().parent / "models" / "model.txt")
        train_auc, test_auc = train_model(feat_csv, model_path)
        generate_dashboard(train_auc, test_auc)
        generate_feature_dashboard(feat_csv)
        pb_path = generate_playbook(feat_csv, model_path)
        update_scoreboard(pb_path, test_auc)
    except Exception as exc:
        agg.flush()
        notifier.send_slack(f"Pipeline failed: {exc}")
        raise

    logging.info("Pipeline completed: %s", pb_path)
    agg.flush()
    notifier.send_slack(f"Pipeline completed: {pb_path}")
    return pb_path


def main(argv: list[str] | None = None) -> None:
    """Entry point for the daily pipeline CLI."""
    config = load_config(argv)
    run(config)


if __name__ == "__main__":
    main()
