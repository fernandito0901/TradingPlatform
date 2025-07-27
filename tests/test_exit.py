import pandas as pd

from models import update_unrealized_pnl
from trading_platform.collector import db


def test_update_unrealized_pnl(tmp_path):
    pf = tmp_path / "portfolio.csv"
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
    conn.execute(
        "INSERT INTO realtime_quotes VALUES (?, ?, ?)",
        ("AAPL", 1, 110.0),
    )
    conn.commit()

    update_unrealized_pnl(conn, str(pf), str(pnl))

    df = pd.read_csv(pnl)
    assert round(df.iloc[0]["unrealized"], 2) == 10.0
    assert df.iloc[0]["realized"] == 0.0
