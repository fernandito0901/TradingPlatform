def test_train_model_importable():
    import importlib

    mod = importlib.import_module("trading_platform.run_daily")
    assert hasattr(mod, "train_model")
