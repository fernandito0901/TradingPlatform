import os
import pytest
from requests import HTTPError

os.environ.setdefault("POLYGON_API_KEY", "x")
os.environ.setdefault("NEWS_API_KEY", "x")
from trading_platform.collector import api


def test_fetch_open_close_no_data(monkeypatch):
    def raise_err(url, params=None):
        raise HTTPError(response=type("R", (), {"status_code": 404})())

    monkeypatch.setattr(api, "rate_limited_get", raise_err)
    with pytest.raises(api.NoData):
        api.fetch_open_close("AAPL", "2025-01-01")


def test_fetch_open_close_success(monkeypatch):
    monkeypatch.setattr(
        api,
        "rate_limited_get",
        lambda url, params=None: {"results": [{"o": 1, "c": 1}]},
    )
    data = api.fetch_open_close("AAPL", "2025-01-01")
    assert data == {"o": 1, "c": 1}
