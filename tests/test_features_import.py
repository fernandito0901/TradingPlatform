def test_features_importable(monkeypatch):
    import importlib

    monkeypatch.setenv("POLYGON_API_KEY", "x")
    mod = importlib.import_module("trading_platform.features")
    assert hasattr(mod, "run_pipeline")
