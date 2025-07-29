"""Minimal feature pipeline using Polygon data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from trading_platform.collector import api
from trading_platform.reports import REPORTS_DIR


class NoData(Exception):
    pass


def fetch_prices(symbol: str, start: str, end: str) -> pd.DataFrame:
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start}/{end}"
    data = api.rate_limited_get(url, {"adjusted": "true", "apiKey": api.API_KEY})
    results = data.get("results", [])
    if not results:
        raise NoData(symbol)
    df = pd.DataFrame(results)
    df.rename(
        columns={"t": "t", "o": "open", "h": "high", "l": "low", "c": "close"},
        inplace=True,
    )
    df["t"] = pd.to_datetime(df["t"], unit="ms").dt.date.astype(str)
    return df[["t", "open", "high", "low", "close"]]


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("t").reset_index(drop=True)
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.rolling(14).mean()
    df["gap_pct"] = df["close"].pct_change()
    df["momentum"] = df["close"].pct_change(5)
    df.dropna(inplace=True)
    return df


def run_pipeline(cfg, symbols: list[str], since: str = "90d") -> str:
    start = (pd.Timestamp.utcnow() - pd.Timedelta(since)).date().isoformat()
    end = pd.Timestamp.utcnow().date().isoformat()
    out_dir = Path(getattr(cfg, "reports_dir", REPORTS_DIR) or REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_frames = []
    for sym in symbols:
        df = fetch_prices(sym, start, end)
        feats = compute_features(df)
        feats["symbol"] = sym
        all_frames.append(feats)
    full = pd.concat(all_frames, ignore_index=True)
    csv_path = out_dir / "features.csv"
    full.to_csv(csv_path, index=False)
    return str(csv_path)
