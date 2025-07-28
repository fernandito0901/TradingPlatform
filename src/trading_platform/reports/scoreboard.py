"""Maintain a historical scoreboard of playbook results."""

from pathlib import Path

import pandas as pd

from . import REPORTS_DIR


def update_scoreboard(
    playbook_path: str,
    auc: float,
    pnl: float | None = None,
    model_path: str | None = None,
    train_auc: float | None = None,
    test_auc: float | None = None,
    cv_auc: float | None = None,
    window_days: int | None = None,
    holdout_auc: float | None = None,
    out_file: str = str(REPORTS_DIR / "scoreboard.csv"),
) -> str:
    """Append a new entry to the scoreboard CSV.

    Parameters
    ----------
    playbook_path : str
        Path to the generated playbook JSON file.
    auc : float
        Model AUC score for the day.
    pnl : float, optional
        Profit and loss from paper trading or backtest.
    out_file : str, optional
        Destination CSV file, by default ``REPORTS_DIR / 'scoreboard.csv'``.

    Returns
    -------
    str
        Path to the updated CSV file.
    """
    date = Path(playbook_path).stem
    entry = {"date": date, "playbook": playbook_path, "auc": auc}
    if pnl is not None:
        entry["pnl"] = pnl
    if model_path is not None:
        entry["model"] = model_path
    if train_auc is not None:
        entry["train_auc"] = train_auc
    if test_auc is not None:
        entry["test_auc"] = test_auc
    if cv_auc is not None:
        entry["cv_auc"] = cv_auc
    if window_days is not None:
        entry["window_days"] = window_days
    if holdout_auc is not None:
        entry["holdout_auc"] = holdout_auc
    entry_df = pd.DataFrame([entry])
    csv_path = Path(out_file)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = pd.concat([df, entry_df], ignore_index=True)
    else:
        df = entry_df
    df.to_csv(csv_path, index=False)
    try:
        from trading_platform.webapp import socketio
    except Exception:
        socketio = None
    if socketio:
        socketio.emit("metric")
    return str(csv_path)


def seed_scoreboard(out_file: str = str(REPORTS_DIR / "scoreboard.csv")) -> str:
    """Ensure scoreboard CSV exists with a dummy row."""

    path = Path(out_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        df = pd.DataFrame(columns=["date", "auc"])
        df.to_csv(path, index=False)
    df = pd.read_csv(path)
    if df.empty:
        df = pd.DataFrame(
            [{"date": pd.Timestamp.utcnow().date().isoformat(), "auc": ""}]
        )
    df.to_csv(path, index=False)
    return str(path)
