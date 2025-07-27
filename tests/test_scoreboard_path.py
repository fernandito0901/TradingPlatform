import os

from trading_platform.webapp import create_app


def test_scoreboard_path(monkeypatch, tmp_path):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    create_app()
    csv = tmp_path / "scoreboard.csv"
    assert csv.exists()
    assert os.access(csv, os.W_OK)
