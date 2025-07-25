"""Trading platform package."""

from .load_env import load_env
from .config import Config, load_config
from . import broker, simulate, strategies, portfolio


def __getattr__(name: str):
    if name == "scheduler":
        from . import scheduler as mod

        return mod
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
]
