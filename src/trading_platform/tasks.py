from __future__ import annotations

from .celery_app import app


@app.task
def dummy_task(secret: str) -> str:
    """Simple task that logs a secret."""
    app.log.get_default_logger().info("secret is %s", secret)
    return secret
