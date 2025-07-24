from pathlib import Path

from reports.strategy_dashboard import generate_strategy_dashboard
from trading_platform import strategies


def test_generate_strategy_dashboard(tmp_path):
    strategies_list = [
        {
            "name": "Call Spread",
            "payoff": lambda s: strategies.call_debit_spread_payoff(s, 100, 110, 5),
            "price": 100,
        }
    ]
    html = generate_strategy_dashboard(
        strategies_list, out_file=str(tmp_path / "dash.html")
    )
    text = Path(html).read_text()
    assert "Strategy Dashboard" in text
    assert "Call Spread" in text
