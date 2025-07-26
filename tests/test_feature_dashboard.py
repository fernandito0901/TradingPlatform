import pandas as pd
from pathlib import Path

from trading_platform.reports.feature_dashboard import generate_feature_dashboard


def test_generate_feature_dashboard(tmp_path):
    df = pd.DataFrame({"t": [1, 2, 3], "close": [1.0, 1.1, 1.2], "rsi14": [30, 40, 50]})
    csv = tmp_path / "features.csv"
    df.to_csv(csv, index=False)
    html = generate_feature_dashboard(str(csv), out_file=str(tmp_path / "dash.html"))
    text = Path(html).read_text()
    assert "html" in text.lower()
