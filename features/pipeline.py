"""Feature engineering pipeline utilities."""

import os
from typing import Optional

from trading_platform.collector.api import (
    fetch_open_close,
    fetch_prev_close,
    fetch_quotes,
    fetch_trades,
)

import pandas as pd
from arch import arch_model


def compute_features(
    df: pd.DataFrame,
    iv: Optional[float] = None,
    news_sent: float = 0.0,
    uoa: float = 0.0,
) -> pd.DataFrame:
    """Compute technical and sentiment features.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing ``close`` prices and ``t`` timestamps.
    iv : float, optional
        30‑day implied volatility. ``None`` inserts ``NaN``.
    news_sent : float, optional
        Aggregate news sentiment score for the symbol.
    uoa : float, optional
        Unusual options activity ratio.

    Returns
    -------
    pandas.DataFrame
        DataFrame with engineered feature columns added.
    """
    df = df.sort_values("t").reset_index(drop=True)
    df["sma20"] = df["close"].rolling(20).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi14"] = 100 - (100 / (1 + rs))
    df["hv30"] = df["close"].pct_change().rolling(30).std() * (252**0.5)
    if iv is not None:
        df["iv30"] = iv
    else:
        df["iv30"] = float("nan")

    ret = df["close"].pct_change().dropna() * 100
    if len(ret) >= 30:
        model = arch_model(ret, p=1, q=1, rescale=False)
        res = model.fit(disp="off")
        vol = res.conditional_volatility / 100
        full = pd.Series(float("nan"), index=df.index)
        full.iloc[-len(vol) :] = vol.values
        df["garch_sigma"] = full
    else:
        df["garch_sigma"] = float("nan")

    df["news_sent"] = news_sent
    df["iv_edge"] = (df["iv30"] - df["hv30"]) / df["hv30"]
    df["garch_spike"] = (df["garch_sigma"] > df["hv30"] * 1.5).astype(float)
    df["uoa"] = uoa
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
    df = df.dropna()
    if df.empty:
        raise ValueError("not enough data for features")
    return df


def from_db(conn, symbol: str) -> pd.DataFrame:
    """Load OHLCV, option, and news data from SQLite and compute features.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open connection to the project database.
    symbol : str
        Symbol to fetch data for.

    Returns
    -------
    pandas.DataFrame
        DataFrame with feature columns computed by :func:`compute_features`.
    """
    query = (
        "SELECT t, open, high, low, close, volume FROM ohlcv WHERE symbol=? ORDER BY t"
    )
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if df.empty:
        raise ValueError("no data for symbol")

    opt = pd.read_sql_query(
        "SELECT iv, volume, open_interest FROM option_chain WHERE symbol=?",
        conn,
        params=(symbol,),
    )
    iv = float(opt["iv"].mean()) if not opt.empty else None
    uoa = 0.0
    if not opt.empty and opt["open_interest"].sum() > 0:
        uoa = opt["volume"].sum() / opt["open_interest"].sum()

    news = pd.read_sql_query(
        "SELECT title FROM news WHERE symbol=?", conn, params=(symbol,)
    )
    news_sent = 0.0
    if not news.empty:
        words_pos = {"up", "gain", "rise", "beat", "soars"}
        words_neg = {"down", "fall", "miss", "drop", "plunge"}
        scores = []
        for title in news["title"]:
            t = title.lower()
            pos = sum(w in t for w in words_pos)
            neg = sum(w in t for w in words_neg)
            scores.append(pos - neg)
        if scores:
            news_sent = sum(scores) / len(scores)

    feats = compute_features(df[["t", "close"]], iv=iv, news_sent=news_sent, uoa=uoa)

    today = pd.Timestamp.utcnow().date().isoformat()
    data = fetch_open_close(symbol, today)
    if not data:
        data = fetch_prev_close(symbol)
    if not data:
        raise ValueError("open/close endpoints returned empty arrays")
    prev_close = data.get("previousClose")
    if prev_close is None:
        results = data.get("results", [])
        if results:
            prev_close = results[0].get("c")
    if prev_close is None:
        raise ValueError("open/close endpoints returned empty arrays")
    open_p = data.get("open") or (data.get("results", [{}])[0].get("o"))
    if open_p is None:
        open_p = float("nan")
    gap = (open_p - prev_close) / prev_close

    df["prev_close"] = df["close"].shift(1)
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["prev_close"]).abs()
    tr3 = (df["low"] - df["prev_close"]).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr14 = tr.rolling(14).mean().iloc[-1]

    try:
        tdata = fetch_trades(symbol)
        tresults = tdata.get("results", [])
        if not tresults:
            raise ValueError
        prices = [
            r.get("p") or r.get("price")
            for r in tresults
            if r.get("p") or r.get("price")
        ]
        sizes = [r.get("s") or r.get("size") or 1 for r in tresults]
        intraday_atr = max(prices) - min(prices)
        vwap = sum(p * s for p, s in zip(prices, sizes)) / sum(sizes)
    except Exception:
        intraday_atr = None
        vwap = None

    try:
        qdata = fetch_quotes(symbol)
        qresults = qdata.get("results", [])
        if not qresults:
            raise ValueError
        spreads = []
        for q in qresults:
            bid = q.get("bp") or q.get("bid_price")
            ask = q.get("ap") or q.get("ask_price")
            if bid is not None and ask is not None:
                spreads.append(ask - bid)
        spread = sum(spreads) / len(spreads) if spreads else None
    except Exception:
        spread = None

    feats["prev_close"] = prev_close
    feats["gap_up"] = max(gap, 0)
    feats["gap_down"] = abs(min(gap, 0))
    feats["atr14"] = atr14
    feats["intraday_atr"] = intraday_atr
    feats["vwap"] = vwap
    feats["spread"] = spread
    return feats


def run_pipeline(conn, symbol: str, out_dir: str = "features") -> str:
    """Run full feature pipeline and write CSV.

    Parameters
    ----------
    conn : sqlite3.Connection
        Database connection with OHLCV data.
    symbol : str
        Ticker symbol to process.
    out_dir : str, optional
        Output directory base, by default ``features``.

    Returns
    -------
    str
        Path to the written CSV file.
    """
    df = from_db(conn, symbol)
    date = pd.Timestamp.utcnow().date().isoformat()
    path = os.path.join(out_dir, date)
    os.makedirs(path, exist_ok=True)
    csv_path = os.path.join(path, "features.csv")
    df.to_csv(csv_path, index=False)
    parquet_path = os.path.join(path, "features.parquet")
    df.to_parquet(parquet_path, index=False)
    return csv_path


__all__ = ["compute_features", "from_db", "run_pipeline"]
