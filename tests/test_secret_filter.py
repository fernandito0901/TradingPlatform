import logging
import os
from trading_platform.secret_filter import SecretFilter


def test_secret_filter_masks_env(caplog):
    os.environ["API_KEY"] = "topsecret"
    logger = logging.getLogger("test")
    logger.addFilter(SecretFilter())
    caplog.set_level(logging.INFO, logger="test")
    logger.info("secret is %s", os.environ["API_KEY"])
    assert "topsecret" not in caplog.text
    assert "****" in caplog.text
