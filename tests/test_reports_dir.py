def test_reports_dir_exists(monkeypatch, tmp_path):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    import importlib

    import trading_platform.reports as reports

    importlib.reload(reports)
    from trading_platform.webapp import create_app

    create_app()
    assert reports.REPORTS_DIR.exists()
