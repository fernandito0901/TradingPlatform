import pandas as pd

from trading_platform import evaluator
from trading_platform.collector import db


def test_evaluate_positions_exit(monkeypatch, tmp_path):
    pf = tmp_path / "pf.csv"
    pnl = tmp_path / "pnl.csv"
    pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "strategy": "s",
                "qty": 1,
                "avg_price": 100,
                "opened_at": "0",
            }
        ]
    ).to_csv(pf, index=False)
    conn = db.init_db(":memory:")
    conn.execute("INSERT INTO realtime_quotes VALUES (?, ?, ?)", ("AAPL", 1, 110.0))
    conn.commit()

    monkeypatch.setattr(evaluator, "notify_position", lambda *a, **k: None)
    monkeypatch.setattr(evaluator.api, "fetch_realtime_quote", lambda *a, **k: None)

    evaluator.evaluate_positions(
        conn, str(pf), str(pnl), stop_loss=0.05, take_profit=0.05
    )

    assert pd.read_csv(pf).empty
    df = pd.read_csv(pnl)
    assert round(df.iloc[0]["realized"], 2) == 10.0
