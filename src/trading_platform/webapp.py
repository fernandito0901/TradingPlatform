"""Simple Flask web interface for running commands."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Thread

from . import scheduler as scheduler_mod
from . import risk_report

import pandas as pd
from flask import Flask, redirect, render_template_string, request, url_for

from .config import load_config
from .run_daily import run as run_daily
from .collector import verify
from .load_env import load_env

SETUP_TEMPLATE = """
<!doctype html>
<title>Setup</title>
<h1>Setup API Keys</h1>
<form method=post>
  <label>Polygon API Key <input name=polygon_api_key></label><br>
  <label>News API Key <input name=news_api_key></label><br>
  <label>Slack Webhook URL <input name=slack_webhook_url></label><br>
  <label>Default Symbols <input name=symbols value="AAPL"></label><br>
  <input type=submit value=Save>
</form>
"""

MAIN_TEMPLATE = """
<!doctype html>
<title>Trading Platform</title>
<h1>Trading Platform</h1>
<form action="{{ url_for('run') }}" method=post>
  <input type=submit value="Run Daily Pipeline">
</form>
<form action="{{ url_for('verify_conn') }}" method=post>
  <input type=submit value="Verify Connectivity">
</form>
<h2>Backfill</h2>
<form action="{{ url_for('backfill_route') }}" method=post>
  <input name=symbol placeholder=Symbol>
  <input name=start placeholder="YYYY-MM-DD">
  <input name=end placeholder="YYYY-MM-DD">
  <input type=submit value=Backfill>
</form>
<h2>Simulate</h2>
<form action="{{ url_for('simulate_route') }}" method=post>
  <input name=csv_file placeholder="Features CSV">
  <input name=capital placeholder=Capital>
  <input type=submit value=Simulate>
</form>
<h2>Dashboards</h2>
<form action="{{ url_for('feature_dash') }}" method=post>
  <input name=csv_file placeholder="Features CSV">
  <input type=submit value="Feature Dashboard">
</form>
<form action="{{ url_for('strategy_dash') }}" method=post>
  <input type=submit value="Strategy Dashboard">
</form>
<h2>Scheduler</h2>
{% if scheduler %}
<p>Scheduler running.</p>
<form action="{{ url_for('stop_scheduler_route') }}" method=post>
  <input type=submit value="Stop Scheduler">
</form>
{% else %}
<form action="{{ url_for('start_scheduler_route') }}" method=post>
  <input type=submit value="Start Scheduler">
</form>
{% endif %}
<h2>Reports</h2>
<ul>
  <li><a href="{{ url_for('static', filename='scoreboard.csv') }}">Scoreboard</a></li>
  <li><a href="{{ url_for('static', filename='dashboard.html') }}">Model Dashboard</a></li>
  <li><a href="{{ url_for('static', filename='feature_dashboard.html') }}">Feature Dashboard</a></li>
  <li><a href="{{ url_for('static', filename='strategies.html') }}">Strategy Dashboard</a></li>
</ul>
{{ scoreboard|safe }}
"""


def create_app(env_path: str | os.PathLike[str] = ".env") -> Flask:
    """Create configured Flask application."""

    app = Flask(__name__, static_folder="reports", static_url_path="/reports")
    app.config["ENV_PATH"] = Path(env_path)
    app.config["SCHED"] = None

    def save_env(data: dict[str, str]) -> None:
        lines = [f"{k}={v}" for k, v in data.items() if v]
        Path(env_path).write_text("\n".join(lines) + "\n")

    def scoreboard_html() -> str:
        csv = Path(app.static_folder) / "scoreboard.csv"
        if not csv.exists():
            return "<p>No results yet</p>"

        df = pd.read_csv(csv)
        if "pnl" in df.columns:
            metrics = risk_report.risk_metrics(str(csv))
            df = df.merge(metrics, on="date", how="left")
        return df.to_html(index=False)

    @app.route("/", methods=["GET", "POST"])
    def index():
        load_env(app.config["ENV_PATH"])
        if request.method == "POST":
            save_env(
                {
                    "POLYGON_API_KEY": request.form.get("polygon_api_key", ""),
                    "NEWS_API_KEY": request.form.get("news_api_key", ""),
                    "SLACK_WEBHOOK_URL": request.form.get("slack_webhook_url", ""),
                    "SYMBOLS": request.form.get("symbols", "AAPL"),
                }
            )
            return redirect(url_for("index"))
        if not os.getenv("POLYGON_API_KEY"):
            return render_template_string(SETUP_TEMPLATE)
        return render_template_string(
            MAIN_TEMPLATE,
            scoreboard=scoreboard_html(),
            scheduler=app.config.get("SCHED") is not None,
        )

    @app.route("/run", methods=["POST"])
    def run():
        cfg = load_config([], env_path=app.config["ENV_PATH"])
        Thread(target=run_daily, args=(cfg,)).start()
        return redirect(url_for("index"))

    @app.route("/verify", methods=["POST"])
    def verify_conn():
        cfg = load_config([], env_path=app.config["ENV_PATH"])
        Thread(target=verify.verify, args=(cfg.symbols,)).start()
        return redirect(url_for("index"))

    @app.route("/start_scheduler", methods=["POST"])
    def start_scheduler_route():
        if app.config.get("SCHED") is None:
            cfg = load_config([], env_path=app.config["ENV_PATH"])
            app.config["SCHED"] = scheduler_mod.start(cfg)
        return redirect(url_for("index"))

    @app.route("/stop_scheduler", methods=["POST"])
    def stop_scheduler_route():
        sched = app.config.pop("SCHED", None)
        if sched is not None:
            sched.shutdown()
        return redirect(url_for("index"))

    @app.route("/backfill", methods=["POST"])
    def backfill_route():
        cfg = load_config([], env_path=app.config["ENV_PATH"])
        symbol = request.form.get("symbol", cfg.symbols.split(",")[0])
        start = request.form.get("start")
        end = request.form.get("end")
        if not start or not end:
            return redirect(url_for("index"))
        from .collector import backfill as backfill_mod, db

        def task() -> None:
            conn = db.init_db(cfg.db_file)
            backfill_mod.fetch_range(conn, symbol, start, end)

        Thread(target=task).start()
        return redirect(url_for("index"))

    @app.route("/simulate", methods=["POST"])
    def simulate_route():
        csv_file = request.form.get("csv_file")
        capital = float(request.form.get("capital", "10000"))
        if not csv_file:
            return redirect(url_for("index"))
        from . import simulate as sim

        Thread(target=sim.simulate, args=(csv_file, "buy_hold", capital)).start()
        return redirect(url_for("index"))

    @app.route("/feature_dashboard", methods=["POST"])
    def feature_dash():
        csv_file = request.form.get("csv_file")
        if not csv_file:
            return redirect(url_for("index"))
        from reports.feature_dashboard import generate_feature_dashboard

        Thread(target=generate_feature_dashboard, args=(csv_file,)).start()
        return redirect(url_for("index"))

    @app.route("/strategy_dashboard", methods=["POST"])
    def strategy_dash():
        from trading_platform import strategies as strat
        from reports.strategy_dashboard import generate_strategy_dashboard

        strategies = [
            {
                "name": "Call Debit Spread",
                "payoff": lambda s: strat.call_debit_spread_payoff(s, 100, 110, 5),
                "price": 100,
            }
        ]

        Thread(target=generate_strategy_dashboard, args=(strategies,)).start()
        return redirect(url_for("index"))

    return app


def main() -> None:
    """Run the Flask development server."""

    app = create_app()
    app.run()


if __name__ == "__main__":
    main()
