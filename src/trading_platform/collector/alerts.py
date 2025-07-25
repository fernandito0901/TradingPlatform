"""Alert aggregation utilities for large trades and news."""

from __future__ import annotations

import os
from typing import List, Optional

from .. import notifier


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

    def flush(self) -> None:
        """Send all queued alerts via Slack and clear the queue."""
        if not self._messages:
            return
        message = "\n".join(self._messages)
        notifier.send_slack(message, webhook_url=self.webhook_url)
        self._messages.clear()


def notify_position(
    symbol: str, action: str, price: float, webhook_url: str | None = None
) -> None:
    """Immediately send a Slack alert for an entry or exit event."""
    notifier.send_slack(f"{action} {symbol} at {price}", webhook_url=webhook_url)
