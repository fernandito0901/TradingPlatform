from pathlib import Path
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, cross_val_score


def train(
    features_csv: str, model_path: str = "models/model.txt", cv: bool = False
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
        Train and test AUC scores. When ``cv`` is ``True`` both values contain
        the mean cross-validation AUC.
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
    if cv:
        model = lgb.LGBMClassifier(objective="binary", verbosity=-1)
        scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
        model.fit(X, y)
        train_auc = float(scores.mean())
        test_auc = train_auc
        booster = model.booster_
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )
        train_set = lgb.Dataset(X_train, label=y_train)
        booster = lgb.train({"objective": "binary", "verbosity": -1}, train_set)
        pred_train = booster.predict(X_train)
        pred_test = booster.predict(X_test)
        train_auc = roc_auc_score(y_train, pred_train)
        test_auc = roc_auc_score(y_test, pred_test)

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    booster.save_model(model_path)
    return train_auc, test_auc
