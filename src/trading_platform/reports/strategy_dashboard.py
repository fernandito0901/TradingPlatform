"""Generate an HTML dashboard summarizing option strategies."""

from pathlib import Path
from typing import Iterable

from trading_platform import strategies as strat

from . import REPORTS_DIR


def generate_strategy_dashboard(
    strategies: Iterable[dict], out_file: str = str(REPORTS_DIR / "strategies.html")
) -> str:
    """Create an interactive dashboard for option strategies.

    Each item in ``strategies`` should contain at minimum ``name`` and ``payoff``
    keys where ``payoff`` is a callable accepting underlying prices.
    The current ``price`` key is used for POP estimation.
    """
    html = [
        "<html><body>",
        "<h1>Strategy Dashboard</h1>",
        "<table>",
        "<tr><th>Name</th><th>POP</th><th>Action</th></tr>",
    ]
    for info in strategies:
        price = info.get("price", 100.0)
        payoff = info["payoff"]
        pop = strat.pop(payoff, price=price)
        html.append(
            f"<tr><td>{info['name']}</td><td>{pop:.2f}</td>"
            f"<td><button>{info.get('action', 'Trade')}</button></td></tr>"
        )
    html.extend(["</table>", "</body></html>"])
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text("\n".join(html))
    return out_file
