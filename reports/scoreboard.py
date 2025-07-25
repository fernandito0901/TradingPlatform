"""Maintain a historical scoreboard of playbook results."""

from pathlib import Path
import pandas as pd


def update_scoreboard(
    playbook_path: str,
    auc: float,
    pnl: float | None = None,
    out_file: str = "reports/scoreboard.csv",
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
        Destination CSV file, by default ``"reports/scoreboard.csv"``.

    Returns
    -------
    str
        Path to the updated CSV file.
    """
    date = Path(playbook_path).stem
    entry = {"date": date, "playbook": playbook_path, "auc": auc}
    if pnl is not None:
        entry["pnl"] = pnl
    entry_df = pd.DataFrame([entry])
    csv_path = Path(out_file)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df = pd.concat([df, entry_df], ignore_index=True)
    else:
        df = entry_df
    df.to_csv(csv_path, index=False)
    return str(csv_path)
