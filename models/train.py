from pathlib import Path
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score


def train(features_csv: str, model_path: str = "models/model.txt") -> float:
    """Train LightGBM model from feature CSV.

    Parameters
    ----------
    features_csv : str
        Path to the features CSV produced by :func:`features.run_pipeline`.
    model_path : str, optional
        Destination path for the trained model.

    Returns
    -------
    float
        AUC score on the training data.
    """
    df = pd.read_csv(features_csv)
    X = df[["sma20", "rsi14"]]
    y = df["target"]
    train_set = lgb.Dataset(X, label=y)
    model = lgb.train({"objective": "binary", "verbosity": -1}, train_set)
    preds = model.predict(X)
    auc = roc_auc_score(y, preds)
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    model.save_model(model_path)
    return auc
