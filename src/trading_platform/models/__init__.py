"""Backwards compatibility wrapper for model training functions."""

from models.train import train
from models.exit import update_unrealized_pnl

__all__ = ["train", "update_unrealized_pnl"]
