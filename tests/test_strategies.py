"""Tests for strategy primitives and POP."""

from trading_platform import strategies


def test_call_debit_spread_payoff():
    payoff = strategies.call_debit_spread_payoff(120, 100, 110, 5)
    assert payoff == 5
    payoff = strategies.call_debit_spread_payoff(105, 100, 110, 5)
    assert payoff == 0
    payoff = strategies.call_debit_spread_payoff(90, 100, 110, 5)
    assert payoff == -5


def test_iron_condor_payoff():
    payoff = strategies.iron_condor_payoff(100, 90, 95, 105, 110, 2)
    assert payoff == 2
    payoff = strategies.iron_condor_payoff(93, 90, 95, 105, 110, 2)
    assert payoff == 0
    payoff = strategies.iron_condor_payoff(120, 90, 95, 105, 110, 2)
    assert payoff == -3


def test_pop_range():
    prob = strategies.pop(
        lambda s: strategies.call_debit_spread_payoff(s, 100, 110, 5),
        price=100,
        sigma=0.1,
        n=1000,
    )
    assert 0.0 <= prob <= 1.0
