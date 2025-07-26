"""Alert aggregation utilities for large trades and news."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from .. import notifier


ALERT_LOG = "reports/alerts.log"


class AlertAggregator:
    """Collect alerts and send them to Slack in batches."""

    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self._messages: List[str] = []

    def add_trade(self, symbol: str, size: int) -> None:
        """Record a large trade alert."""
        self._messages.append(f"Large trade {symbol} size {size}")

    def add_news(self, title: str, url: str) -> None:
        """Record a news headline alert."""
        self._messages.append(f"News: {title} {url}")

    def add_position(self, symbol: str, action: str, price: float) -> None:
        """Record an entry or exit alert."""
        self._messages.append(f"{action} {symbol} at {price}")

    def _write_log(self, message: str) -> None:
        Path(ALERT_LOG).parent.mkdir(parents=True, exist_ok=True)
        with open(ALERT_LOG, "a") as f:
            f.write(message + "\n")

    def flush(self) -> None:
        """Send all queued alerts via Slack and clear the queue."""
        if not self._messages:
            return
        lines = ["Alerts:"] + [f"- {m}" for m in self._messages]
        message = "\n".join(lines)
        notifier.send_slack(message, webhook_url=self.webhook_url)
        self._write_log(message)
        self._messages.clear()


def notify_position(
    symbol: str, action: str, price: float, webhook_url: str | None = None
) -> None:
    """Immediately send a Slack alert for an entry or exit event."""
    msg = f"{action} {symbol} at {price}"
    notifier.send_slack(msg, webhook_url=webhook_url)
    Path(ALERT_LOG).parent.mkdir(parents=True, exist_ok=True)
    with open(ALERT_LOG, "a") as f:
        f.write(msg + "\n")
