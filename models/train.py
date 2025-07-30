from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import lightgbm as lgb
import optuna
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split

BEST_PARAMS_FILE = Path("models/best_params.json")


@dataclass
class TrainResult:
    train_auc: float
    test_auc: float
    cv_auc: float
    holdout_auc: float
    model_path: str
    metadata_path: str
    params: dict[str, Any]
    window_days: int


def _read_features(path: str) -> pd.DataFrame:
    file = Path(path)
    if file.suffix == ".parquet":
        df = pd.read_parquet(file)
    else:
        df = pd.read_csv(file)
    if "t" in df.columns:
        df["t"] = pd.to_datetime(df["t"])
    return df


def _load_best_params(symbol: str) -> dict[str, Any] | None:
    if BEST_PARAMS_FILE.exists():
        data = json.loads(BEST_PARAMS_FILE.read_text())
        return data.get(symbol)
    return None


def _save_best_params(symbol: str, params: dict[str, Any]) -> None:
    data: dict[str, Any] = {}
    if BEST_PARAMS_FILE.exists():
        data = json.loads(BEST_PARAMS_FILE.read_text())
    data[symbol] = params
    BEST_PARAMS_FILE.write_text(json.dumps(data, indent=2))


def optimize_hyperparams(X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    """Return best LightGBM hyperparameters using Optuna."""

    def objective(trial: optuna.trial.Trial) -> float:
        params = {
            "objective": "binary",
            "verbosity": -1,
            "num_leaves": trial.suggest_int("num_leaves", 16, 64),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
        }
        model = lgb.LGBMClassifier(**params)
        scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")
        return float(scores.mean())

    study = optuna.create_study(
        direction="maximize",
        study_name="lgbm_opt",
        storage="sqlite:///optuna.db",
        load_if_exists=True,
    )
    study.optimize(objective, n_trials=100, show_progress_bar=False)
    return study.best_params


def train(
    features_csv: str,
    model_dir: str = "models",
    cv: bool = False,
    feature_cols: list[str] | None = None,
    window_days: int = 60,
    tune: bool = False,
    symbol: str = "model",
) -> TrainResult:
    """Train LightGBM model from features file with rolling window and drift guard."""

    df = _read_features(features_csv)
    if df.empty:
        raise ValueError("no feature rows available")
    if "target" not in df.columns:
        df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
        df.dropna(subset=["target"], inplace=True)

    cutoff = df["t"].max() - timedelta(days=window_days)
    df = df[df["t"] >= cutoff]
    if df.empty:
        raise ValueError("not enough rows for window")

    if feature_cols is None:
        feature_cols = [c for c in df.columns if c not in {"t", "target"}]
    X = df[feature_cols]
    y = df["target"]

    params = _load_best_params(symbol) or {}
    base = {"objective": "binary", "verbosity": -1}

    # cross-validate with existing params
    cv_auc = float(
        cross_val_score(
            lgb.LGBMClassifier(**base, **params), X, y, cv=5, scoring="roc_auc"
        ).mean()
    )
    if tune or cv_auc < 0.70:
        params = optimize_hyperparams(X, y)
        _save_best_params(symbol, params)
        cv_auc = float(
            cross_val_score(
                lgb.LGBMClassifier(**base, **params), X, y, cv=5, scoring="roc_auc"
            ).mean()
        )

    holdout_cut = df["t"].max() - timedelta(days=5)
    holdout = df[df["t"] > holdout_cut]
    train_df = df[df["t"] <= holdout_cut]
    X_train, X_test, y_train, y_test = train_test_split(
        train_df[feature_cols], train_df["target"], test_size=0.25, random_state=42
    )
    train_set = lgb.Dataset(X_train, label=y_train)
    booster = lgb.train({**base, **params}, train_set)

    pred_train = booster.predict(X_train)
    pred_test = booster.predict(X_test)
    train_auc = roc_auc_score(y_train, pred_train)
    test_auc = roc_auc_score(y_test, pred_test)

    holdout_auc = 0.0
    if not holdout.empty:
        pred_holdout = booster.predict(holdout[feature_cols])
        holdout_auc = roc_auc_score(holdout["target"], pred_holdout)

    model_dir_path = Path(model_dir)
    model_dir_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    model_path = model_dir_path / f"{symbol}_{timestamp}.pkl"
    booster.save_model(model_path)

    features_hash = hashlib.sha256(Path(features_csv).read_bytes()).hexdigest()
    metadata = {
        "features_hash": features_hash,
        "params": params,
        "cv_auc": cv_auc,
        "train_auc": train_auc,
        "test_auc": test_auc,
        "holdout_auc": holdout_auc,
        "window_days": window_days,
        "model": str(model_path),
    }
    metadata_path = model_path.with_name(model_path.stem + "_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2))

    # drift guard check against previous model
    previous = sorted(model_dir_path.glob("model_*_metadata.json"))
    if len(previous) > 1:
        with open(previous[-2]) as f:
            prev = json.load(f)
        prev_auc = float(prev.get("holdout_auc", 1.0))
        if holdout_auc < 0.65 or holdout_auc < prev_auc * 0.95:
            print(
                f"CRITICAL: holdout AUC {holdout_auc:.3f} dropped from {prev_auc:.3f}; skipping deployment"
            )
            return TrainResult(
                train_auc, test_auc, cv_auc, holdout_auc, "", "", params, window_days
            )

    return TrainResult(
        train_auc,
        test_auc,
        cv_auc,
        holdout_auc,
        str(model_path),
        str(metadata_path),
        params,
        window_days,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train LightGBM model")
    parser.add_argument("features_csv")
    parser.add_argument("--window-days", type=int, default=60)
    parser.add_argument("--tune", action="store_true")
    parser.add_argument("--symbol", default="model")
    parser.add_argument("--model-dir", default="models")
    args = parser.parse_args(argv)
    res = train(
        args.features_csv,
        model_dir=args.model_dir,
        window_days=args.window_days,
        tune=args.tune,
        symbol=args.symbol,
    )
    print(json.dumps(res.__dict__, indent=2))


if __name__ == "__main__":
    main()
