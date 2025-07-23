import json
from pathlib import Path
import pandas as pd
import lightgbm as lgb


def generate_playbook(
    features_csv: str, model_file: str, out_dir: str = "playbooks"
) -> str:
    """Generate daily options trade playbook.

    Parameters
    ----------
    features_csv : str
        Path to the engineered features CSV.
    model_file : str
        Path to the trained LightGBM model.
    out_dir : str, optional
        Output directory for playbook JSON, by default ``playbooks``.

    Returns
    -------
    str
        Path to the written JSON playbook.
    """
    df = pd.read_csv(features_csv)
    model = lgb.Booster(model_file=model_file)
    X = df[["sma20", "rsi14"]]
    prob_up = model.predict(X)
    momentum = (df["close"] - df["sma20"]) / df["sma20"]
    df["score"] = 2.5 * prob_up + 1.5 * momentum
    top = df.nlargest(5, "score")

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    date = pd.Timestamp.utcnow().date().isoformat()
    path = Path(out_dir) / f"{date}.json"
    payload = {
        "date": date,
        "trades": top[["t", "score"]].to_dict(orient="records"),
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return str(path)
