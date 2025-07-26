"""Tests for playbook generation."""

from pathlib import Path
import json
import pandas as pd
import lightgbm as lgb

from trading_platform.playbook import generate_playbook


def test_generate_playbook(tmp_path):
    df = pd.DataFrame(
        {
            "t": [1, 2, 3, 4],
            "close": [10, 11, 12, 13],
            "sma20": [10, 10.5, 11, 11.5],
            "rsi14": [50, 55, 60, 65],
            "iv_edge": [0.1, 0.2, 0.1, 0.3],
            "uoa": [0.0, 1.0, 0.0, 1.0],
            "garch_spike": [0.0, 0.0, 1.0, 0.0],
            "news_sent": [0.2, 0.1, -0.1, 0.0],
            "target": [0, 1, 0, 1],
        }
    )
    feat_csv = tmp_path / "features.csv"
    df.to_csv(feat_csv, index=False)

    feature_cols = [
        "sma20",
        "rsi14",
        "iv_edge",
        "uoa",
        "garch_spike",
        "news_sent",
    ]
    train_set = lgb.Dataset(df[feature_cols], label=df["target"])
    model = lgb.train(
        {"objective": "binary", "verbosity": -1}, train_set, num_boost_round=2
    )
    model_file = tmp_path / "model.txt"
    model.save_model(model_file)

    out_dir = tmp_path / "playbooks"
    path = generate_playbook(str(feat_csv), str(model_file), str(out_dir))

    prob_up = model.predict(df[feature_cols])
    momentum = (df["close"] - df["sma20"]) / df["sma20"]
    expected = df.copy()
    expected["prob_up"] = prob_up
    expected["momentum"] = momentum
    expected["score"] = (
        2.5 * prob_up
        + 1.5 * momentum
        + df["news_sent"]
        + df["iv_edge"]
        + df["uoa"]
        - df["garch_spike"]
    )
    expected_top = (
        expected.nlargest(5, "score")[
            [
                "t",
                "score",
                "prob_up",
                "momentum",
                "news_sent",
                "iv_edge",
                "uoa",
                "garch_spike",
            ]
        ]
        .round(4)
    )

    pb = json.loads(Path(path).read_text())
    assert pb["date"]
    assert isinstance(pb["trades"], list)
    assert len(pb["trades"]) <= 5
    assert pb["trades"] == expected_top.to_dict(orient="records")


def test_generate_playbook_missing_columns(tmp_path):
    df = pd.DataFrame(
        {
            "t": [1, 2],
            "close": [10, 11],
            "sma20": [10, 10.5],
            "rsi14": [50, 55],
            "iv_edge": [0.1, 0.2],
            "target": [0, 1],
        }
    )

    feature_cols = ["sma20", "rsi14", "iv_edge"]
    train_set = lgb.Dataset(df[feature_cols], label=df["target"])
    model = lgb.train(
        {"objective": "binary", "verbosity": -1}, train_set, num_boost_round=2
    )
    model_file = tmp_path / "model.txt"
    model.save_model(model_file)

    # Drop one feature to simulate a pipeline that didn't produce it
    test_df = df.drop(columns=["iv_edge"])
    feat_csv = tmp_path / "features.csv"
    test_df.to_csv(feat_csv, index=False)

    out_dir = tmp_path / "playbooks"
    path = generate_playbook(str(feat_csv), str(model_file), str(out_dir))

    filled = test_df.copy()
    filled["iv_edge"] = 0
    prob_up = model.predict(filled[feature_cols])
    momentum = (filled["close"] - filled["sma20"]) / filled["sma20"]
    expected = filled.copy()
    expected["prob_up"] = prob_up
    expected["momentum"] = momentum
    expected["news_sent"] = filled.get("news_sent", 0)
    expected["uoa"] = filled.get("uoa", 0)
    expected["garch_spike"] = filled.get("garch_spike", 0)
    expected["score"] = (
        2.5 * prob_up
        + 1.5 * momentum
        + filled.get("news_sent", 0)
        + filled["iv_edge"]
        + filled.get("uoa", 0)
        - filled.get("garch_spike", 0)
    )
    expected_top = (
        expected.nlargest(5, "score")[
            [
                "t",
                "score",
                "prob_up",
                "momentum",
                "news_sent",
                "iv_edge",
                "uoa",
                "garch_spike",
            ]
        ]
        .round(4)
    )

    pb = json.loads(Path(path).read_text())
    assert pb["trades"] == expected_top.to_dict(orient="records")
