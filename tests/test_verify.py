import importlib
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from trading_platform.collector import verify


def test_verify_success(monkeypatch):
    importlib.reload(verify)

    calls = []

    def fake_fetch_ohlcv(conn, sym):
        calls.append(f"ohlcv-{sym}")

    def fake_fetch_option_chain(conn, sym):
        calls.append(f"chain-{sym}")

    monkeypatch.setattr(verify.api, "fetch_ohlcv", fake_fetch_ohlcv)
    monkeypatch.setattr(verify.api, "fetch_option_chain", fake_fetch_option_chain)

    result = verify.verify("AAPL,MSFT")
    assert result is True
    assert calls == ["ohlcv-AAPL", "chain-AAPL", "ohlcv-MSFT", "chain-MSFT"]


def test_verify_failure(monkeypatch):
    importlib.reload(verify)

    def bad_fetch(conn, sym):
        raise RuntimeError("fail")

    monkeypatch.setattr(verify.api, "fetch_ohlcv", bad_fetch)
    monkeypatch.setattr(verify.api, "fetch_option_chain", lambda conn, sym: None)

    result = verify.verify("AAPL")
    assert result is False
