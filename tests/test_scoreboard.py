"""Tests for scoreboard utilities."""

import pandas as pd

from reports.scoreboard import update_scoreboard


def test_update_scoreboard(tmp_path):
    pb1 = tmp_path / "2025-01-01.json"
    pb1.write_text("{}")
    csv = tmp_path / "board.csv"
    path = update_scoreboard(
        str(pb1),
        0.7,
        pnl=1.5,
        out_file=str(csv),
        model_path="m1.txt",
        train_auc=0.8,
        holdout_auc=0.75,
    )
    df = pd.read_csv(path)
    assert df.iloc[0]["playbook"] == str(pb1)
    assert df.iloc[0]["auc"] == 0.7
    assert df.iloc[0]["pnl"] == 1.5

    pb2 = tmp_path / "2025-01-02.json"
    pb2.write_text("{}")
    update_scoreboard(
        str(pb2),
        0.8,
        pnl=2.0,
        out_file=str(csv),
        model_path="m2.txt",
        train_auc=0.9,
        holdout_auc=0.8,
    )
    df = pd.read_csv(csv)
    assert len(df) == 2
    assert df.iloc[1]["date"] == "2025-01-02"
    assert df.iloc[1]["pnl"] == 2.0
