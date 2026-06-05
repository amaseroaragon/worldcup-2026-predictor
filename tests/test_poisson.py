import pytest

from src.prediction.core.poisson import (
    expected_goals_from_elo,
    poisson_probability,
    recent_form_multiplier,
    score_matrix,
    score_probability,
    squad_strength_multiplier,
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


def test_expected_goals_include_attack_and_opponent_defense_ratings():
    goals_a, goals_b = expected_goals_from_elo(
        1500,
        1500,
        attack_rating_a=1.2,
        defense_rating_a=0.8,
        attack_rating_b=0.9,
        defense_rating_b=1.1,
    )

    assert goals_a == pytest.approx(1.35 * 1.2 * 1.1)
    assert goals_b == pytest.approx(1.35 * 0.9 * 0.8)


def test_expected_goals_applies_bounds_after_strength_ratings():
    goals_a, goals_b = expected_goals_from_elo(
        1500,
        1500,
        attack_rating_a=10.0,
        defense_rating_a=0.01,
        attack_rating_b=0.01,
        defense_rating_b=10.0,
    )

    assert goals_a == 3.5
    assert goals_b == 0.2


def test_expected_goals_rejects_non_positive_strength_rating():
    with pytest.raises(ValueError, match="attack and defense ratings"):
        expected_goals_from_elo(1500, 1500, attack_rating_a=0.0)


def test_expected_goals_include_recent_form_multiplier():
    goals_a, goals_b = expected_goals_from_elo(
        1500,
        1500,
        form_rating_a=1.2,
        form_rating_b=0.8,
    )

    assert goals_a == pytest.approx(1.35 * (1 + 0.15 * 0.2))
    assert goals_b == pytest.approx(1.35 * (1 + 0.15 * -0.2))


def test_expected_goals_include_squad_strength_multiplier():
    goals_a, goals_b = expected_goals_from_elo(
        1500,
        1500,
        squad_strength_rating_a=1.15,
        squad_strength_rating_b=0.85,
    )

    assert goals_a == pytest.approx(1.35 * (1 + 0.10 * 0.15))
    assert goals_b == pytest.approx(1.35 * (1 + 0.10 * -0.15))


def test_recent_form_multiplier_uses_neutral_fallback():
    assert recent_form_multiplier(None) == 1.0


def test_recent_form_multiplier_can_be_disabled(monkeypatch):
    monkeypatch.setattr("src.prediction.core.poisson.USE_RECENT_FORM", False)

    assert recent_form_multiplier(1.2) == 1.0


def test_squad_strength_multiplier_uses_neutral_fallback():
    assert squad_strength_multiplier(None) == 1.0


def test_squad_strength_multiplier_can_be_disabled(monkeypatch):
    monkeypatch.setattr("src.prediction.core.poisson.USE_SQUAD_STRENGTH", False)

    assert squad_strength_multiplier(1.15) == 1.0


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
