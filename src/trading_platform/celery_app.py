from __future__ import annotations

from celery import Celery

from .secret_filter import SecretFilter

app = Celery("trading_platform")
app.conf.update(task_always_eager=True)
app.log.get_default_logger().addFilter(SecretFilter())


@app.on_after_configure.connect
def setup_logging(sender, **kwargs):
    sender.log.get_default_logger().addFilter(SecretFilter())
