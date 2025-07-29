from datetime import datetime
from trading_platform.collector import api


def test_is_equity_session_false(monkeypatch):
    fake_now = datetime(2025, 1, 1, 2, 0, tzinfo=api.EASTERN)
    monkeypatch.delenv("TESTING", raising=False)
    assert not api.is_equity_session(fake_now)


def test_skip_fetch_if_closed(monkeypatch):
    called = False

    def fake_get(url, params=None):
        nonlocal called
        called = True
        raise AssertionError("should not be called")

    monkeypatch.setattr(api, "is_equity_session", lambda now=None: False)
    monkeypatch.setattr(api.requests, "get", fake_get)
    api.fetch_trades("AAPL")
    assert not called
