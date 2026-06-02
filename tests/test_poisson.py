import pytest

from src.prediction.poisson import (
    expected_goals_from_elo,
    poisson_probability,
    score_matrix,
    score_probability,
)


def test_poisson_probability_valid_value():
    prob = poisson_probability(k=1, lambda_=1.35)

    assert 0 < prob < 1


def test_poisson_probability_rejects_negative_goals():
    with pytest.raises(ValueError):
        poisson_probability(k=-1, lambda_=1.35)


def test_poisson_probability_rejects_non_positive_lambda():
    with pytest.raises(ValueError):
        poisson_probability(k=1, lambda_=0)


def test_expected_goals_equal_elos_are_equal():
    goals_a, goals_b = expected_goals_from_elo(1500, 1500)

    assert goals_a == pytest.approx(goals_b)
    assert goals_a == pytest.approx(1.35)


def test_expected_goals_favor_stronger_team():
    goals_a, goals_b = expected_goals_from_elo(1700, 1500)

    assert goals_a > goals_b


def test_expected_goals_are_bounded():
    goals_a, goals_b = expected_goals_from_elo(3000, 500)

    assert 0.2 <= goals_a <= 3.5
    assert 0.2 <= goals_b <= 3.5


def test_score_probability_valid_value():
    prob = score_probability(
        goals_a=1,
        goals_b=0,
        expected_goals_a=1.35,
        expected_goals_b=1.10,
    )

    assert 0 < prob < 1


def test_score_matrix_dimensions():
    matrix = score_matrix(
        expected_goals_a=1.35,
        expected_goals_b=1.10,
        max_goals=5,
    )

    assert len(matrix) == 6
    assert len(matrix[0]) == 6


def test_score_matrix_probability_mass_is_reasonable():
    matrix = score_matrix(
        expected_goals_a=1.35,
        expected_goals_b=1.10,
        max_goals=10,
    )

    total_prob = sum(sum(row) for row in matrix)

    assert total_prob == pytest.approx(1.0, abs=0.01)