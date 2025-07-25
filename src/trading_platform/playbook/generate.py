import json
from pathlib import Path
import pandas as pd
import lightgbm as lgb


def generate_playbook(
    features_csv: str, model_file: str, out_dir: str = "playbooks"
) -> str:
    """Generate daily options trade playbook.

    The scoring rule ranks trades using model predictions and
    additional context features:

    ``score = 2.5 * prob_up + 1.5 * momentum + news_sent + iv_edge + uoa - garch_spike``.

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

    model_features = list(model.feature_name())
    for feat in model_features:
        if feat not in df.columns:
            df[feat] = 0

    X = df[model_features]
    prob_up = model.predict(X)
    momentum = (df["close"] - df["sma20"]) / df["sma20"]
    news_sent = df.get("news_sent", 0)
    iv_edge = df.get("iv_edge", 0)
    uoa = df.get("uoa", 0)
    garch_spike = df.get("garch_spike", 0)
    df["score"] = (
        2.5 * prob_up + 1.5 * momentum + news_sent + iv_edge + uoa - garch_spike
    )
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
