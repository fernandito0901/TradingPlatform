"""Tests for Slack notifier."""

from types import SimpleNamespace

import pytest

from trading_platform import notifier


def test_send_slack_skip(caplog, monkeypatch):
    caplog.set_level("WARNING")
    notifier.send_slack("hi", webhook_url=None)
    assert "SLACK_WEBHOOK_URL not set" in caplog.text


def test_send_slack_success(monkeypatch):
    calls = {}

    def fake_post(url, json=None, timeout=10):
        calls["url"] = url
        calls["payload"] = json
        return SimpleNamespace(status_code=200, raise_for_status=lambda: None)

    monkeypatch.setattr(notifier.requests, "post", fake_post)
    notifier.send_slack("msg", webhook_url="http://example.com")
    assert calls["url"] == "http://example.com"
    assert calls["payload"] == {"text": "msg"}


def test_send_slack_error(monkeypatch):
    def fake_post(url, json=None, timeout=10):
        raise ValueError("boom")

    monkeypatch.setattr(notifier.requests, "post", fake_post)
    with pytest.raises(Exception):
        notifier.send_slack("msg", webhook_url="http://example.com")
