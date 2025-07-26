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
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="/reports/style.css">
  <!-- Plotly loaded on demand -->
  <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
  <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js\"></script>
</head>
<body class="p-3">
<nav class="navbar navbar-expand-lg bg-light mb-3 rounded shadow-sm px-3">
  <a class="navbar-brand" href="#">Trading AI</a>
  <div class="ms-auto">
    <button class="btn btn-outline-secondary me-2" onclick="toggleDark()"><i class="fa fa-moon"></i></button>
    <div class="dropdown d-inline">
      <button class="btn btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">Settings</button>
      <ul class="dropdown-menu dropdown-menu-end">
        <li><a class="dropdown-item" href="#" onclick="startRun()">Run Daily Pipeline</a></li>
        <li><a class="dropdown-item" href="#" onclick="verifyConn()">Verify Connectivity</a></li>
      </ul>
    </div>
  </div>
</nav>
<div class="container-fluid">
  <div class="row row-cols-lg-3 row-cols-1 g-3">
    <div class="col-lg-3">
      <div class="card p-3 shadow-sm mb-3" id="trades-card">
        <h5 class="card-title"><i class="fa fa-lightbulb me-2"></i>Recommended Trades</h5>
        <table class="table table-striped small" id="trades">
          <thead class="table-light">
            <tr>
              <th role="button" onclick="sortTrades('t')">Ticker</th>
              <th role="button" onclick="sortTrades('strategy')">Strategy</th>
              <th role="button" onclick="sortTrades('pop')">POP</th>
              <th role="button" onclick="sortTrades('score')">Score</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
        <div id="trades-loading" class="text-muted">Loading…</div>
        <div id="trades-upd" class="small text-muted"></div>
      </div>
      <div class="card p-3 shadow-sm mb-3" id="news-card">
        <div class="d-flex justify-content-between mb-2">
          <h5 class="card-title mb-0"><i class="fa fa-newspaper me-2"></i>News</h5>
          <div>
            <button class="btn btn-sm btn-outline-secondary me-1" onclick="clearNews()">Clear All</button>
            <button class="btn btn-sm btn-outline-secondary" onclick="markNewsRead()">Mark All as Read</button>
          </div>
        </div>
        <ul id="news" class="list-unstyled mb-0"></ul>
        <div id="news-empty" class="text-muted">Loading…</div>
        <div id="news-upd" class="small text-muted"></div>
      </div>
      <div class="card p-3 shadow-sm" id="watch-card">
        <h5 class="card-title"><i class="fa fa-eye me-2"></i>Watchlist</h5>
        <ul id="watchlist" class="list-unstyled"></ul>
      </div>
    </div>
    <div class="col-lg-5">
      <div class="card p-3 shadow-sm mb-3" id="metrics-card">
        <h5 class="card-title"><i class="fa fa-chart-line me-2"></i>Metrics</h5>
        <div id="metrics"></div>
        <div id="metrics-empty" class="text-muted">Loading…</div>
        <div id="metrics-upd" class="small text-muted"></div>
      </div>
      <div class="card p-3 shadow-sm" id="equity-card">
        <h5 class="card-title"><i class="fa fa-chart-area me-2"></i>Equity Curve</h5>
        <div id="equity"></div>
        <div id="equity-upd" class="small text-muted"></div>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="card p-3 shadow-sm mb-3" id="overview-card">
        <h5 class="card-title"><i class="fa fa-chart-pie me-2"></i>Market Overview</h5>
        <table class="table table-sm" id="overview"></table>
        <div id="overview-empty" class="text-muted">Loading…</div>
        <div id="overview-upd" class="small text-muted"></div>
      </div>
      <div class="card p-3 shadow-sm" id="alerts-card">
        <div class="d-flex justify-content-between mb-2">
          <h5 class="card-title mb-0"><i class="fa fa-bell me-2"></i>Notifications</h5>
          <div>
            <button class="btn btn-sm btn-outline-secondary me-1" onclick="clearAlerts()">Clear All</button>
            <button class="btn btn-sm btn-outline-secondary" onclick="markAlertsRead()">Mark Read</button>
          </div>
        </div>
        <div id="alerts" class="toast-container position-static"></div>
      </div>
    </div>
  </div>
  <div class="mt-4" id="scheduler-section">
    <h5><i class="fa fa-calendar me-2"></i>Scheduler</h5>
    {% if scheduler %}
    <form action="{{ url_for('stop_scheduler_route') }}" method=post>
      <input type=submit value="Stop Scheduler" class="btn btn-warning">
    </form>
    {% else %}
    <form action="{{ url_for('start_scheduler_route') }}" method=post>
      <input type=submit value="Start Scheduler" class="btn btn-success">
    </form>
    {% endif %}
  </div>
  <div class="mt-4">
    <h5>Scoreboard</h5>
    {{ scoreboard|safe }}
  </div>
</div>
<script>
const socket=io();
socket.on('trade',t=>addTradeRow(t));
socket.on('pnl_update',d=>showEquity(d));
socket.on('overview_quote',q=>updateOverview(q));
let seenAlerts=new Set();
let seenNews=new Set();
let trades=[];
let sortKey='score';
let sortAsc=false;
function toggleDark(){
  const dark=document.body.classList.toggle('bg-dark');
  document.body.classList.toggle('text-white');
  localStorage.setItem('dark',dark);
}
if(localStorage.getItem('dark')==='true'){
  document.body.classList.add('bg-dark','text-white');
}
function startRun(){fetch('/run',{method:'POST'})}
function verifyConn(){fetch('/verify',{method:'POST'})}
function load(){
  fetch('/api/trades').then(r=>r.json()).then(showTrades);
  fetch('/api/metrics').then(r=>r.json()).then(showMetrics);
  fetch('/api/positions').then(r=>r.json()).then(showPositions);
  fetch('/api/watchlist').then(r=>r.json()).then(showWatchlist);
  fetch('/api/overview').then(r=>r.json()).then(showOverview);
}
function refreshNews(){fetch('/api/news').then(r=>r.json()).then(showNews);}
function refreshAlerts(){fetch('/api/alerts').then(r=>r.json()).then(showAlerts);}
function renderTrades(){
  const tbl=document.getElementById('trades').querySelector('tbody');
  if(!tbl)return;
  const rows=[...trades];
  rows.sort((a,b)=>{
    let av=a[sortKey]??'';let bv=b[sortKey]??'';
    if(typeof av==='string') return av.localeCompare(bv)*(sortAsc?1:-1);
    return (av-bv)*(sortAsc?1:-1);
  });
  tbl.innerHTML=rows.map(d=>{
    const prob=isNaN(d.prob_up)?0:d.prob_up*100;
    const score=isNaN(d.score)?'—':d.score.toFixed(2);
    const bar=`<div class="progress"><div class="progress-bar bg-success text-dark" role="progressbar" aria-valuenow="${prob.toFixed(0)}" aria-valuemin="0" aria-valuemax="100" style="width:${prob.toFixed(0)}%">${prob.toFixed(0)}%</div></div>`;
    return `<tr><td>${d.t}</td><td>${d.strategy||'Spread'}</td><td>${bar}</td><td>${score}</td></tr>`;
  }).join('');
}
function sortTrades(key){
  if(sortKey===key){sortAsc=!sortAsc;}else{sortKey=key;sortAsc=false;}
  renderTrades();
}
function showTrades(data){
  document.getElementById('trades-loading').style.display='none';
  document.getElementById('trades-card').style.display='block';
  trades=data;renderTrades();
  document.getElementById('trades-upd').textContent='Last updated '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function addTradeRow(d){
  trades.unshift(d);renderTrades();
}
function showNews(data){
  const ul=document.getElementById('news');
  const empty=document.getElementById('news-empty');
  empty.style.display='none';
  data.forEach(n=>{
    const id=n.url+(n.published_at||'');
    if(seenNews.has(id)) return;
    seenNews.add(id);
    const li=document.createElement('li');
    li.innerHTML=`<a href="${n.url}" target="_blank">${n.title}</a>`;
    ul.prepend(li);
    while(ul.children.length>5) ul.lastElementChild.remove();
  });
  empty.style.display=ul.children.length? 'none':'block';
  document.getElementById('news-upd').textContent='Last updated '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function badge(v){
  if(v>0.8) return `<span class="badge bg-success">${v.toFixed(2)}</span>`;
  if(v>=0.7) return `<span class="badge bg-warning text-dark">${v.toFixed(2)}</span>`;
  return `<span class="badge bg-danger">${v.toFixed(2)}</span>`;
}
function showMetrics(m){
  const div=document.getElementById('metrics');
  const empty=document.getElementById('metrics-empty');
  document.getElementById('metrics-card').style.display='block';
  if(m.status==='empty'||!m.train_auc){div.innerHTML='';empty.style.display='block';return;}
  empty.style.display='none';
  div.innerHTML=`Last trained ${m.date||''}<br>Train ${badge(m.train_auc)} Test ${badge(m.test_auc)} CV ${badge(m.cv_auc)}`;
  document.getElementById('metrics-upd').textContent='Last updated '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function showPositions(data){
  const tbl=document.getElementById('positions');
  if(!data.length){tbl.innerHTML='';return;}
  tbl.innerHTML='<tr><th>Symbol</th><th>Qty</th><th>Avg Price</th></tr>'+data.map(p=>`<tr><td>${p.symbol}</td><td>${p.qty}</td><td>${p.avg_price}</td></tr>`).join('');
}
function showWatchlist(list){
  const ul=document.getElementById('watchlist');
  ul.innerHTML=list.map(s=>`<li>${s}</li>`).join('');
}
function showOverview(data){
  const tbl=document.getElementById('overview');
  const empty=document.getElementById('overview-empty');
  if(data.status==='empty'){document.getElementById('overview-card').style.display='none';return;}
  if(!data.length){tbl.innerHTML='';empty.style.display='block';return;}
  empty.style.display='none';
  document.getElementById('overview-card').style.display='block';
  tbl.innerHTML='<tr><th>Symbol</th><th>Close</th></tr>'+data.map(d=>`<tr data-sym="${d.ticker||d.symbol}"><td>${d.ticker||d.symbol}</td><td>${d.close}</td></tr>`).join('');
  document.getElementById('overview-upd').textContent='Last updated '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function updateOverview(q){
  const tbl=document.getElementById('overview');
  const empty=document.getElementById('overview-empty');
  empty.style.display='none';
  let row=tbl.querySelector(`tr[data-sym="${q.symbol}"]`);
  if(!row){
    row=document.createElement('tr');
    row.dataset.sym=q.symbol;
    row.innerHTML=`<td>${q.symbol}</td><td>${q.p}</td>`;
    tbl.appendChild(row);
  }else{
    row.children[1].textContent=q.p;
  }
  document.getElementById('overview-upd').textContent='Last updated '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
function showAlerts(msgs){
  const container=document.getElementById('alerts');
  msgs.forEach(m=>{
    if(seenAlerts.has(m)) return;
    seenAlerts.add(m);
    const toast=document.createElement('div');
    toast.className='toast align-items-center text-bg-info border-0';
    toast.innerHTML=`<div class="d-flex"><div class="toast-body text-truncate">${m}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    container.prepend(toast);
    if(container.children.length>5) container.lastElementChild.remove();
    new bootstrap.Toast(toast,{delay:5000}).show();
  });
}
function showEquity(data){
  if(!data.length){return;}
  const trace={x:data.map(r=>r.date),y:data.map(r=>r.total),type:'scatter'};
  Plotly.newPlot('equity',[trace]);
  document.getElementById('equity-upd').textContent='Last updated '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}
let plotlyLoaded=false;
function refreshEquity(){
  if(!plotlyLoaded){
    const s=document.createElement('script');
    s.src='https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.24.1';
    s.onload=()=>{plotlyLoaded=true; fetch('/api/pnl').then(r=>r.json()).then(showEquity);};
    document.head.appendChild(s);
  }else{
    fetch('/api/pnl').then(r=>r.json()).then(showEquity);
  }
}
function clearAlerts(){document.getElementById('alerts').innerHTML='';seenAlerts.clear();}
function markAlertsRead(){clearAlerts();}
function clearNews(){document.getElementById('news').innerHTML='';seenNews.clear();document.getElementById('news-empty').style.display='block';}
function markNewsRead(){
  document.querySelectorAll('#news a').forEach(a=>seenNews.add(a.href));
}
load();
refreshNews();
refreshAlerts();
const obs=new IntersectionObserver(e=>{if(e[0].isIntersecting){refreshEquity();obs.disconnect();}},{});
obs.observe(document.getElementById('equity'));
setInterval(load,10000);
setInterval(refreshNews,300000);
setInterval(refreshAlerts,300000);
setInterval(refreshEquity,600000);
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
<h2>Back-test</h2>
<form action="{{ url_for('simulate_route') }}" method=get>
  <input name=days placeholder=Days>
  <input type=submit value="Run Back-test">
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

    @app.route("/simulate", methods=["GET"])
    def simulate_route():
        days = int(request.args.get("days", "30"))
        csv_file = latest_file("features", ".csv")
        model_path = latest_file("models", ".txt")
        if not csv_file or not model_path:
            return redirect(url_for("index"))
        from . import backtest as bt

        Thread(target=bt.backtest, args=(csv_file, model_path, days)).start()
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
        trades = data.get("trades", [])
        for t in trades:
            for k, v in t.items():
                if isinstance(v, float):
                    t[k] = round(v, 4)
        return jsonify(trades)

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
            return jsonify({"status": "empty"})
        df = pd.read_csv(csv)
        last = df.iloc[-1]
        if all(
            pd.isna(last.get(col)) for col in ["train_auc", "test_auc", "cv_auc", "auc"]
        ):
            return jsonify({"status": "empty"})
        res = {
            "date": last.get("date", ""),
            "train_auc": float(last.get("train_auc", last.get("auc", 0))),
            "test_auc": float(last.get("test_auc", 0)),
            "cv_auc": float(last.get("cv_auc", 0)),
        }
        return jsonify(res)

    @app.route("/api/features/latest")
    def api_features_latest():
        feat = latest_file("features", ".csv")
        meta = latest_file("models", "_metadata.json")
        if not feat or not meta:
            return jsonify({})
        data = json.loads(Path(meta).read_text())
        data["features"] = feat
        return jsonify(data)

    @app.route("/api/scoreboard")
    def api_scoreboard():
        csv = Path(app.static_folder) / "scoreboard.csv"
        if not csv.exists():
            return jsonify([])
        df = pd.read_csv(csv)
        return jsonify(df.to_dict(orient="records"))

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
            try:
                from .collector.api import fetch_snapshot_tickers

                data = fetch_snapshot_tickers()
                return jsonify(data.get("tickers", []))
            except Exception:
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
        if df.empty:
            try:
                from .collector.api import fetch_snapshot_tickers

                data = fetch_snapshot_tickers()
                return jsonify(data.get("tickers", []))
            except Exception:
                return jsonify([])
        return jsonify(df.to_dict(orient="records"))

    @app.route("/api/options/<date>")
    def api_options(date: str):
        path = Path(app.static_folder) / f"options_chain.{date}.csv"
        if not path.exists():
            return jsonify([])
        df = pd.read_csv(path)
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
