"""Strategy performance metrics."""

from __future__ import annotations

import pandas as pd


def sharpe_ratio(returns: pd.Series) -> float:
    """Compute the Sharpe ratio of a return series."""
    if returns.empty:
        return 0.0
    excess = returns - returns.mean()
    std = returns.std(ddof=0)
    if std == 0:
        return 0.0
    return (excess.mean() / std) * (len(returns) ** 0.5)


def sortino_ratio(returns: pd.Series, target: float = 0.0) -> float:
    """Compute the Sortino ratio with respect to ``target``."""
    if returns.empty:
        return 0.0
    downside = returns[returns < target] - target
    if downside.empty:
        return float("inf")
    denom = (downside.pow(2).mean()) ** 0.5
    if denom == 0:
        return float("inf")
    return (returns.mean() - target) / denom


def win_rate(returns: pd.Series) -> float:
    """Fraction of periods with positive returns."""
    if returns.empty:
        return 0.0
    return (returns > 0).sum() / len(returns)
