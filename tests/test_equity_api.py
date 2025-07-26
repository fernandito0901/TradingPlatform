from pathlib import Path
from trading_platform.webapp import create_app
import pandas as pd


def test_api_equity_last(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "pnl.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-02"], "total": [1, 2]})
    df.to_csv(csv, index=False)
    import trading_platform.portfolio as pf

    pf.load_pnl = lambda path=pf.PNL_FILE: pd.read_csv(csv)
    client = app.test_client()
    resp = client.get("/api/metrics/equity?last=400d")
    assert resp.status_code == 200
    assert len(resp.json) == 2


def test_api_equity_empty(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    app.static_folder = str(tmp_path)
    csv = Path(app.static_folder) / "pnl.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    csv.write_text("date,total\n")
    import trading_platform.portfolio as pf

    pf.load_pnl = lambda path=pf.PNL_FILE: pd.read_csv(csv)
    client = app.test_client()
    resp = client.get("/api/metrics/equity")
    assert resp.status_code == 200
    assert resp.json == []
