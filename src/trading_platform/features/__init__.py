"""Backwards compatibility wrapper for feature functions."""

import importlib


def __getattr__(name: str):
    if name in {"run_pipeline", "compute_features", "from_db", "pipeline"}:
        pipeline = importlib.import_module("features.pipeline")
        return pipeline if name == "pipeline" else getattr(pipeline, name)
    raise AttributeError(name)


__all__ = ["run_pipeline", "compute_features", "from_db", "pipeline"]
