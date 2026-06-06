import pytest

from src.backtesting.metrics import (
    brier_champion,
    champion_rank,
    real_champion_probability,
    top_k_hit,
)


PROBABILITY_ROWS = [
    {"team": "Brazil", "champion_probability": 0.40},
    {"team": "France", "champion_probability": 0.30},
    {"team": "Argentina", "champion_probability": 0.20},
    {"team": "Spain", "champion_probability": 0.10},
]


def test_champion_rank_returns_one_based_rank():
    assert champion_rank(PROBABILITY_ROWS, "Argentina") == 3


def test_real_champion_probability_returns_assigned_probability():
    assert real_champion_probability(PROBABILITY_ROWS, "France") == pytest.approx(0.30)


def test_top_k_hit_checks_real_champion_in_top_k():
    assert top_k_hit(PROBABILITY_ROWS, "Argentina", 3) is True
    assert top_k_hit(PROBABILITY_ROWS, "Argentina", 2) is False


def test_brier_champion_returns_mean_binary_brier_score():
    assert brier_champion(PROBABILITY_ROWS, "France") == pytest.approx(
        ((0.40 - 0.0) ** 2 + (0.30 - 1.0) ** 2 + 0.20**2 + 0.10**2) / 4
    )

