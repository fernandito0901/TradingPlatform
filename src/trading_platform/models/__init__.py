"""Wrapper module for backward compatibility."""

from importlib import import_module
from typing import Any

_mod = import_module("models")
__all__ = getattr(_mod, "__all__", [])


def __getattr__(name: str) -> Any:
    return getattr(_mod, name)
