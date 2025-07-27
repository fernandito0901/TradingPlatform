import pandas as pd

from features import load_pipeline


def test_load_pipeline_callable():
    assert callable(load_pipeline)


def test_run_pipeline(monkeypatch, tmp_path):
    from features import pipeline

    def fake_get(url, params=None):
        return {
            "results": [
                {"t": 0, "o": 1, "h": 1, "l": 1, "c": 1},
                {"t": 86400000, "o": 2, "h": 2, "l": 2, "c": 2},
            ]
        }

    monkeypatch.setattr(pipeline.api, "rate_limited_get", fake_get)
    cfg = type("C", (), {"reports_dir": tmp_path})
    out = pipeline.run_pipeline(cfg, ["AAPL"], since="1d")
    df = pd.read_csv(out)
    assert set(["atr14", "gap_pct", "momentum"]).issubset(df.columns)
