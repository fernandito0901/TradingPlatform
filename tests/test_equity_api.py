import os
from pathlib import Path

import pandas as pd

from trading_platform.webapp import create_app


def test_api_equity_last(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    csv = Path(os.environ["REPORTS_DIR"]) / "pnl.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    csv.unlink(missing_ok=True)
    df = pd.DataFrame({"date": ["2025-01-01", "2025-01-02"], "pnl": [1, 2]})
    df.to_csv(csv, index=False)
    client = app.test_client()
    resp = client.get("/api/metrics/equity?last=400d")
    assert resp.status_code == 200
    assert len(resp.json) == 2


def test_api_equity_empty(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POLYGON_API_KEY=x\n")
    app = create_app(env_path=env)
    csv = Path(os.environ["REPORTS_DIR"]) / "pnl.csv"
    csv.parent.mkdir(parents=True, exist_ok=True)
    csv.unlink(missing_ok=True)
    csv.write_text("date,pnl\n")
    client = app.test_client()
    resp = client.get("/api/metrics/equity")
    assert resp.status_code == 200
    assert resp.json == []
