"""Tests for environment loader."""

import importlib
import os
import sys
from importlib import reload

load_env_module = importlib.import_module("trading_platform.load_env")


def test_load_env_sets_environ(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    monkeypatch.chdir(tmp_path)
    reload(sys.modules["trading_platform.load_env"])
    load_env_module.load_env(env_file)
    assert os.environ.get("FOO") == "bar"
    assert os.environ.get("BAZ") == "qux"
