import logging
import os
import re


class SecretFilter(logging.Filter):
    """Mask sensitive values in log records."""

    _vars = ["API_KEY", "NEWS_API_KEY", "SLACK_WEBHOOK_URL"]

    def __init__(self) -> None:
        pattern = "|".join(
            re.escape(os.getenv(v, "")) for v in self._vars if os.getenv(v)
        )
        self.regex = re.compile(pattern) if pattern else None
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        if self.regex is None:
            return True
        if isinstance(record.msg, str):
            record.msg = self.regex.sub("****", record.msg)
        if record.args:
            record.args = tuple(self.regex.sub("****", str(a)) for a in record.args)
        return True
