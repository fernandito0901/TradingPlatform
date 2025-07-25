"""Options strategy primitives and POP estimator."""

from __future__ import annotations

import numpy as np


def call_debit_spread_payoff(
    s: float | np.ndarray,
    long_strike: float,
    short_strike: float,
    debit: float,
) -> np.ndarray:
    """Payoff of a call debit spread at expiration.

    Parameters
    ----------
    s : float or ndarray
        Underlying price(s) at expiration.
    long_strike : float
        Strike of the purchased call.
    short_strike : float
        Strike of the written call.
    debit : float
        Net premium paid for the spread.

    Returns
    -------
    ndarray
        Profit or loss for each price in ``s``.
    """
    s = np.asarray(s)
    payoff = np.maximum(s - long_strike, 0) - np.maximum(s - short_strike, 0) - debit
    return payoff


def iron_condor_payoff(
    s: float | np.ndarray,
    long_put: float,
    short_put: float,
    short_call: float,
    long_call: float,
    credit: float,
) -> np.ndarray:
    """Payoff of a short iron condor strategy at expiration.

    Parameters
    ----------
    s : float or ndarray
        Underlying price(s) at expiration.
    long_put : float
        Strike of the protective long put.
    short_put : float
        Strike of the sold put.
    short_call : float
        Strike of the sold call.
    long_call : float
        Strike of the protective long call.
    credit : float
        Net premium received from opening the position.

    Returns
    -------
    ndarray
        Profit or loss for each price in ``s``.
    """
    s = np.asarray(s)
    put_loss = np.maximum(short_put - s, 0) - np.maximum(long_put - s, 0)
    call_loss = np.maximum(s - short_call, 0) - np.maximum(s - long_call, 0)
    payoff = credit - put_loss - call_loss
    return payoff


def pop(
    payoff_fn,
    price: float,
    *,
    sigma: float = 0.2,
    n: int = 10000,
    **kwargs,
) -> float:
    """Estimate probability of profit using Monte Carlo sampling.

    Parameters
    ----------
    payoff_fn : callable
        Function returning payoff for a vector of underlying prices.
    price : float
        Current underlying price.
    sigma : float, optional
        Volatility used for the log-normal price simulation.
    n : int, optional
        Number of Monte Carlo samples.
    **kwargs :
        Additional arguments passed to ``payoff_fn``.

    Returns
    -------
    float
        Estimated probability of profit between 0 and 1.
    """
    mean = np.log(price)
    sims = np.random.lognormal(mean=mean - 0.5 * sigma**2, sigma=sigma, size=n)
    profits = payoff_fn(sims, **kwargs)
    return float((profits > 0).mean())
