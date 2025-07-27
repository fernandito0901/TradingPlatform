"""Trading platform package."""

import importlib

from .config import Config, load_config
from .load_env import load_env


def __getattr__(name: str):
    modules = {
        "broker",
        "simulate",
        "strategies",
        "portfolio",
        "backtest",
        "metrics",
        "risk_report",
        "scheduler",
        "evaluator",
    }
    if name in modules:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(name)


__all__ = [
    "load_env",
    "Config",
    "load_config",
    "broker",
    "simulate",
    "strategies",
    "portfolio",
    "backtest",
    "metrics",
    "risk_report",
    "scheduler",
    "evaluator",
]
