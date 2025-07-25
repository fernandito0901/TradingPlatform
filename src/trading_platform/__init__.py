"""Trading platform package."""

from .load_env import load_env
from .config import Config, load_config
from . import broker, simulate, strategies, portfolio
from . import risk_report


import importlib


def __getattr__(name: str):
    if name in {"scheduler", "evaluator"}:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(name)


__all__ = [
    "load_env",
    "Config",
    "load_config",
    "simulate",
    "strategies",
    "broker",
    "portfolio",
    "scheduler",
    "risk_report",
    "evaluator",
]
