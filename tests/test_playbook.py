from pathlib import Path
import json
import pandas as pd
import lightgbm as lgb
from playbook import generate_playbook


def test_generate_playbook(tmp_path):
    df = pd.DataFrame(
        {
            "t": [1, 2, 3, 4],
            "close": [10, 11, 12, 13],
            "sma20": [10, 10.5, 11, 11.5],
            "rsi14": [50, 55, 60, 65],
            "target": [0, 1, 0, 1],
        }
    )
    feat_csv = tmp_path / "features.csv"
    df.to_csv(feat_csv, index=False)

    train_set = lgb.Dataset(df[["sma20", "rsi14"]], label=df["target"])
    model = lgb.train(
        {"objective": "binary", "verbosity": -1}, train_set, num_boost_round=2
    )
    model_file = tmp_path / "model.txt"
    model.save_model(model_file)

    out_dir = tmp_path / "playbooks"
    path = generate_playbook(str(feat_csv), str(model_file), str(out_dir))

    pb = json.loads(Path(path).read_text())
    assert pb["date"]
    assert isinstance(pb["trades"], list)
    assert len(pb["trades"]) <= 5
