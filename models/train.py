from pathlib import Path
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


def train(
    features_csv: str, model_path: str = "models/model.txt"
) -> tuple[float, float]:
    """Train LightGBM model from feature CSV with train/test split.

    Parameters
    ----------
    features_csv : str
        Path to the features CSV produced by :func:`features.run_pipeline`.
    model_path : str, optional
        Destination path for the trained model.

    Returns
    -------
    tuple[float, float]
        Train and test AUC scores.
    """
    df = pd.read_csv(features_csv)
    feature_cols = [
        c
        for c in [
            "sma20",
            "rsi14",
            "iv30",
            "hv30",
            "garch_sigma",
            "news_sent",
        ]
        if c in df.columns
    ]
    X = df[feature_cols]
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    train_set = lgb.Dataset(X_train, label=y_train)
    model = lgb.train({"objective": "binary", "verbosity": -1}, train_set)
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)
    train_auc = roc_auc_score(y_train, pred_train)
    test_auc = roc_auc_score(y_test, pred_test)
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    model.save_model(model_path)
    return train_auc, test_auc
