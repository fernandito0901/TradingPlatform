import pandas as pd
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from trading_platform.models import train as train_model


def test_train_model(tmp_path):
    data = {
        "sma20": [1, 2, 3, 4, 5, 6],
        "rsi14": [40, 50, 60, 55, 65, 70],
        "target": [0, 1, 0, 1, 0, 1],
    }
    df = pd.DataFrame(data)
    fpath = tmp_path / "features.csv"
    df.to_csv(fpath, index=False)
    model_path = tmp_path / "model.txt"
    train_auc, test_auc = train_model(str(fpath), str(model_path))
    assert 0.0 <= train_auc <= 1.0
    assert 0.0 <= test_auc <= 1.0
    assert model_path.exists()
