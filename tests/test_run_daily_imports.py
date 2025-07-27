
def test_train_model_importable(monkeypatch):
    import importlib

    monkeypatch.setenv("POLYGON_API_KEY", "x")
    monkeypatch.setenv("NEWS_API_KEY", "y")
    mod = importlib.import_module("trading_platform.run_daily")
    assert hasattr(mod, "train_model")
