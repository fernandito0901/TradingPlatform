import pandas as pd
from models import train as train_model


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
    auc = train_model(str(fpath), str(model_path))
    assert 0.0 <= auc <= 1.0
    assert model_path.exists()
