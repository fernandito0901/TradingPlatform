def test_reports_importable():
    import importlib

    module = importlib.import_module("trading_platform.reports.scoreboard")
    assert module is not None
