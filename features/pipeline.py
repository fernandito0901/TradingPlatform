import os
import pandas as pd


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute SMA20 and RSI14 indicators.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing a ``close`` price column and ``t`` timestamps.

    Returns
    -------
    pandas.DataFrame
        DataFrame with ``sma20``, ``rsi14`` and ``target`` columns added.
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
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
    return df.dropna()


def from_db(conn, symbol: str) -> pd.DataFrame:
    """Load OHLCV data for ``symbol`` from SQLite and compute features."""
    query = "SELECT t, close FROM ohlcv WHERE symbol=? ORDER BY t"
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if df.empty:
        raise ValueError("no data for symbol")
    return compute_features(df)


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
    return csv_path
