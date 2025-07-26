from __future__ import annotations

import pandas as pd


def fetch_flow(symbol: str) -> pd.DataFrame:
    """Return placeholder unusual options flow."""
    return pd.DataFrame([{"symbol": symbol, "call_ratio": 0.0, "put_ratio": 0.0}])
