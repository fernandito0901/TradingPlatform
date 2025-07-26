"""Tests for alert aggregator utilities."""

import importlib

from trading_platform.collector import alerts


def test_alert_aggregator_flush(monkeypatch, tmp_path):
    importlib.reload(alerts)
    monkeypatch.setattr(alerts, "ALERT_LOG", str(tmp_path / "alerts.log"))
    agg = alerts.AlertAggregator(webhook_url="http://example.com")
    sent = []
    monkeypatch.setattr(
        alerts.notifier, "send_slack", lambda msg, webhook_url=None: sent.append(msg)
    )
    agg.add_trade("AAPL", 10000)
    agg.add_news("Headline", "http://news")
    agg.add_position("AAPL", "EXIT", 99.5)
    agg.flush()
    assert sent
    msg = sent[0]
    assert msg.startswith("Alerts:")
    assert "- Large trade AAPL" in msg
    assert "- News: Headline" in msg
    assert (tmp_path / "alerts.log").exists()
    assert agg._messages == []


def test_notify_position(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setattr(alerts, "ALERT_LOG", str(tmp_path / "alerts.log"))
    monkeypatch.setattr(
        alerts.notifier, "send_slack", lambda msg, webhook_url=None: sent.append(msg)
    )
    alerts.notify_position("AAPL", "ENTER", 101)
    assert "ENTER AAPL" in sent[0]
    assert (tmp_path / "alerts.log").exists()
