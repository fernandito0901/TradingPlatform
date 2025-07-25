"""Tests for alert aggregator utilities."""

import importlib

from trading_platform.collector import alerts


def test_alert_aggregator_flush(monkeypatch):
    importlib.reload(alerts)
    agg = alerts.AlertAggregator(webhook_url="http://example.com")
    sent = []
    monkeypatch.setattr(
        alerts.notifier, "send_slack", lambda msg, webhook_url=None: sent.append(msg)
    )
    agg.add_trade("AAPL", 10000)
    agg.add_news("Headline", "http://news")
    agg.flush()
    assert sent
    assert "AAPL" in sent[0] and "Headline" in sent[0]
    assert agg._messages == []
