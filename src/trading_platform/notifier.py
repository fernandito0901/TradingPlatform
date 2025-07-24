import logging
import os
from typing import Optional

import requests


def send_slack(message: str, webhook_url: Optional[str] = None) -> None:
    """Send a Slack notification if configured.

    Parameters
    ----------
    message : str
        Text message to send to the Slack channel.
    webhook_url : str, optional
        Incoming webhook URL. Defaults to ``SLACK_WEBHOOK_URL`` environment
        variable.
    """
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        logging.warning("SLACK_WEBHOOK_URL not set; skipping Slack notification")
        return

    try:
        resp = requests.post(url, json={"text": message}, timeout=10)
        resp.raise_for_status()
    except Exception as exc:  # pragma: no cover - log only
        logging.error("Failed to send Slack message: %s", exc)
        raise
