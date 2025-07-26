"""Simple Flask web interface for running commands."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Thread
import json
import sqlite3

from . import risk_report

import pandas as pd
from flask import (
    Flask,
    redirect,
    render_template_string,
    request,
    url_for,
    jsonify,
)
from flask_socketio import SocketIO

socketio = SocketIO()

from .config import load_config
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

DASH_TEMPLATE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=utf-8>
  <meta name=viewport content=\"width=device-width, initial-scale=1\">
  <title>Trading AI Dashboard</title>
  <link rel=\"icon\" href=\"/reports/favicon.ico\">
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap\" rel=\"stylesheet\">
  <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\">
  <script src=\"https://cdn.jsdelivr.net/npm/plotly.js-dist@2.24.1\"></script>
  <script src=\"https://cdn.socket.io/4.5.4/socket.io.min.js\"></script>
  <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>
</head>
<body class=\"p-3\">
<div class=\"container-fluid\">
  <h1 class=\"mb-4\">Trading Dashboard</h1>
  <div class=\"mb-3\">
    <button class=\"btn btn-primary me-2\" onclick=\"fetch('/run',{method:'POST'})\">Run Daily Pipeline</button>
    <button class=\"btn btn-secondary me-2\" onclick=\"fetch('/verify',{method:'POST'})\">Verify Connectivity</button>
    <button class=\"btn btn-outline-dark\" onclick=\"toggleDark()\">Dark Mode</button>
  </div>
  <div class=\"row\">
    <div class=\"col-md-4\">
      <h2>Recommended Trades</h2>
      <table class=\"table\" id=\"trades\"></table>
      <h2>News</h2>
      <div class=\"d-flex justify-content-end mb-2\">
        <button class=\"btn btn-sm btn-outline-secondary me-2\" onclick=\"clearNews()\">Clear All</button>
        <button class=\"btn btn-sm btn-outline-secondary\" onclick=\"markNewsRead()\">Mark All as Read</button>
      </div>
      <ul id=\"news\"></ul>
      <h2>Watchlist</h2>
      <ul id=\"watchlist\"></ul>
    </div>
    <div class=\"col-md-4\">
      <h2>Metrics</h2>
      <div id=\"metrics\"></div>
      <h2>Open Positions</h2>
      <table class=\"table\" id=\"positions\"></table>
    </div>
    <div class=\"col-md-4\">
      <h2>Market Overview</h2>
      <table class=\"table\" id=\"overview\"></table>
    </div>
  </div>
  <h2 class=\"mt-4\">Equity Curve</h2>
  <div id=\"equity\"></div>
  <h2 class=\"mt-4\">Scheduler</h2>
  {% if scheduler %}
  <form action="{{ url_for('stop_scheduler_route') }}" method=post>
    <input type=submit value="Stop Scheduler" class="btn btn-warning">
  </form>
  {% else %}
  <form action="{{ url_for('start_scheduler_route') }}" method=post>
    <input type=submit value="Start Scheduler" class="btn btn-success">
  </form>
  {% endif %}
  <h2 class=\"mt-4\">Scoreboard</h2>
  {{ scoreboard|safe }}
  <div class="d-flex justify-content-end mb-2">
    <button class="btn btn-sm btn-outline-secondary me-2" onclick="clearAlerts()">Clear All</button>
    <button class="btn btn-sm btn-outline-secondary" onclick="markAlertsRead()">Mark All as Read</button>
  </div>
  <div id=\"alerts\" class=\"toast-container position-fixed top-0 end-0 p-3\"></div>
</div>
<script>
const socket=io();
socket.on('trade',t=>addTradeRow(t));
let seenAlerts=new Set();
let seenNews=new Set();
function toggleDark(){
  document.body.classList.toggle('bg-dark');
  document.body.classList.toggle('text-white');
}
function load(){
  fetch('/api/trades').then(r=>r.json()).then(showTrades);
  fetch('/api/metrics').then(r=>r.json()).then(showMetrics);
  fetch('/api/positions').then(r=>r.json()).then(showPositions);
  fetch('/api/pnl').then(r=>r.json()).then(showEquity);
  fetch('/api/watchlist').then(r=>r.json()).then(showWatchlist);
  fetch('/api/overview').then(r=>r.json()).then(showOverview);
}
function refreshNews(){fetch('/api/news').then(r=>r.json()).then(showNews);}
function refreshAlerts(){fetch('/api/alerts').then(r=>r.json()).then(showAlerts);}
function showTrades(data){
  const tbl=document.getElementById('trades');
  tbl.innerHTML='<tr><th>Ticker</th><th>Strategy</th><th>POP</th><th>Score</th></tr>'+data.map(d=>`<tr><td>${d.t}</td><td>${d.strategy||'Spread'}</td><td><div class="progress"><div class="progress-bar" style="width:${(d.prob_up*100).toFixed(0)}%"></div></div></td><td>${d.score.toFixed(2)}</td></tr>`).join('');
}
function addTradeRow(d){
  const tbl=document.getElementById('trades');
  const row=document.createElement('tr');
  row.innerHTML=`<td>${d.t}</td><td>${d.strategy||'Spread'}</td><td><div class="progress"><div class="progress-bar" style="width:${(d.prob_up*100).toFixed(0)}%"></div></div></td><td>${d.score.toFixed(2)}</td>`;
  tbl.prepend(row);
}
function showNews(data){
  const ul=document.getElementById('news');
  data.forEach(n=>{
    if(seenNews.has(n.url)) return;
    seenNews.add(n.url);
    const li=document.createElement('li');
    li.innerHTML=`<a href="${n.url}" target="_blank">${n.title}</a>`;
    ul.prepend(li);
  });
}
function showMetrics(m){
  document.getElementById('metrics').innerHTML=`<strong>Model ${m.date||''}</strong><br>Train AUC: ${m.train_auc??''} Test AUC: ${m.test_auc??''} CV AUC: ${m.cv_auc??''}`;
}
function showPositions(data){
  const tbl=document.getElementById('positions');
  tbl.innerHTML='<tr><th>Symbol</th><th>Qty</th><th>Avg Price</th></tr>'+data.map(p=>`<tr><td>${p.symbol}</td><td>${p.qty}</td><td>${p.avg_price}</td></tr>`).join('');
}
function showWatchlist(list){
  const ul=document.getElementById('watchlist');
  ul.innerHTML=list.map(s=>`<li>${s}</li>`).join('');
}
function showOverview(data){
  const tbl=document.getElementById('overview');
  tbl.innerHTML='<tr><th>Symbol</th><th>Close</th></tr>'+data.map(d=>`<tr><td>${d.symbol}</td><td>${d.close}</td></tr>`).join('');
}
function showAlerts(msgs){
  msgs.forEach(m=>{
    if(seenAlerts.has(m)) return;
    seenAlerts.add(m);
    const container=document.getElementById('alerts');
    const toast=document.createElement('div');
    toast.className='toast align-items-center text-bg-info border-0';
    toast.innerHTML=`<div class="d-flex"><div class="toast-body">${m}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    container.appendChild(toast);
    new bootstrap.Toast(toast,{delay:5000}).show();
  });
}
function showEquity(data){
  if(!data.length){return;}
  const trace={x:data.map(r=>r.date),y:data.map(r=>r.total),type:'scatter'};
  Plotly.newPlot('equity',[trace]);
}
function clearAlerts(){document.getElementById('alerts').innerHTML='';}
function markAlertsRead(){seenAlerts.clear();clearAlerts();}
function clearNews(){document.getElementById('news').innerHTML='';seenNews.clear();}
function markNewsRead(){
  document.querySelectorAll('#news a').forEach(a=>seenNews.add(a.href));
}
load();
refreshNews();
refreshAlerts();
setInterval(load,10000);
setInterval(refreshNews,300000);
setInterval(refreshAlerts,300000);
</script>
</body></html>
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
  <input name=capital placeholder=Capital>
  <input type=submit value=Simulate>
</form>
<h2>Dashboards</h2>
<form action="{{ url_for('feature_dash') }}" method=post>
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
    socketio.init_app(app)
    app.config["ENV_PATH"] = Path(env_path)
    app.config["SCHED"] = None

    # ensure scoreboard CSV and placeholder reports exist to avoid broken links
    sb_csv = Path(app.static_folder) / "scoreboard.csv"
    if not sb_csv.exists():
        sb_csv.parent.mkdir(parents=True, exist_ok=True)
        if not sb_csv.exists():
            sb_csv.write_text("date,playbook,auc\n")

    for name in ["dashboard.html", "feature_dashboard.html", "strategies.html"]:
        path = Path(app.static_folder) / name
        if not path.exists():
            path.write_text("<p>No report yet</p>")

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

    def latest_file(folder: str, ext: str) -> str | None:
        path = Path(folder)
        if not path.exists():
            return None
        files = sorted(path.glob(f"*{ext}"), reverse=True)
        return str(files[0]) if files else None

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
            DASH_TEMPLATE,
            scoreboard=scoreboard_html(),
            scheduler=app.config.get("SCHED") is not None,
        )

    @app.route("/run", methods=["POST"])
    def run():
        from .run_daily import run as run_daily

        cfg = load_config([], env_path=app.config["ENV_PATH"])
        Thread(target=run_daily, args=(cfg,)).start()
        return redirect(url_for("index"))

    @app.route("/verify", methods=["POST"])
    def verify_conn():
        from .collector import verify as verify_mod

        cfg = load_config([], env_path=app.config["ENV_PATH"])
        Thread(target=verify_mod.verify, args=(cfg.symbols,)).start()
        return redirect(url_for("index"))

    @app.route("/start_scheduler", methods=["POST"])
    def start_scheduler_route():
        if app.config.get("SCHED") is None:
            from . import scheduler as scheduler_mod

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
        csv_file = request.form.get("csv_file") or latest_file("features", ".csv")
        capital = float(request.form.get("capital", "10000"))
        if not csv_file:
            return redirect(url_for("index"))
        from . import simulate as sim

        Thread(target=sim.simulate, args=(csv_file, "buy_hold", capital)).start()
        return redirect(url_for("index"))

    @app.route("/feature_dashboard", methods=["POST"])
    def feature_dash():
        csv_file = request.form.get("csv_file") or latest_file("features", ".csv")
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

    @app.route("/api/trades")
    def api_trades():
        pb = latest_file("playbooks", ".json")
        if not pb:
            return jsonify([])
        data = json.loads(Path(pb).read_text())
        return jsonify(data.get("trades", []))

    @app.route("/api/news")
    def api_news():
        db_path = "market_data.db"
        if not Path(db_path).exists():
            return jsonify([])
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(
            "SELECT title, url FROM news ORDER BY published_at DESC LIMIT 5", conn
        )
        conn.close()
        return jsonify(df.to_dict(orient="records"))

    @app.route("/api/metrics")
    def api_metrics():
        csv = Path(app.static_folder) / "scoreboard.csv"
        if not csv.exists():
            return jsonify({})
        df = pd.read_csv(csv)
        last = df.iloc[-1]
        res = {
            "date": last.get("date", ""),
            "train_auc": float(last.get("train_auc", last.get("auc", 0))),
            "test_auc": float(last.get("test_auc", 0)),
            "cv_auc": float(last.get("cv_auc", 0)),
        }
        return jsonify(res)

    @app.route("/api/positions")
    def api_positions():
        from . import portfolio

        df = portfolio.load_portfolio()
        return jsonify(df.to_dict(orient="records"))

    @app.route("/api/pnl")
    def api_pnl():
        from . import portfolio

        df = portfolio.load_pnl()
        return jsonify(df.to_dict(orient="records"))

    @app.route("/api/alerts")
    def api_alerts():
        from .collector import alerts as alert_mod

        path = Path(alert_mod.ALERT_LOG)
        if not path.exists():
            return jsonify([])
        lines = path.read_text().strip().splitlines()[-5:]
        return jsonify(lines)

    @app.route("/api/watchlist")
    def api_watchlist():
        path = Path(app.config["ENV_PATH"])
        syms = []
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("SYMBOLS="):
                    syms = line.split("=", 1)[1].split(",")
                    break
        if not syms:
            syms = os.getenv("SYMBOLS", "AAPL").split(",")
        return jsonify(syms)

    @app.route("/api/overview")
    def api_overview():
        path = Path(app.config["ENV_PATH"])
        db_path = "market_data.db"
        if not Path(db_path).exists():
            return jsonify([])
        conn = sqlite3.connect(db_path)
        syms = []
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("SYMBOLS="):
                    syms = line.split("=", 1)[1].split(",")
                    break
        if not syms:
            syms = os.getenv("SYMBOLS", "AAPL").split(",")
        query = (
            "SELECT symbol, close FROM ohlcv WHERE t=(SELECT MAX(t) FROM ohlcv) "
            "AND symbol IN (%s)" % ",".join("?" * len(syms))
        )
        df = pd.read_sql(query, conn, params=syms)
        conn.close()
        return jsonify(df.to_dict(orient="records"))

    @socketio.on("connect")
    def on_connect():
        pass

    return app


def main() -> None:
    """Run the Flask development server."""

    app = create_app()
    host = os.getenv("WEBAPP_HOST", "0.0.0.0")
    port = int(os.getenv("WEBAPP_PORT", "5000"))
    socketio.run(app, host=host, port=port, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
