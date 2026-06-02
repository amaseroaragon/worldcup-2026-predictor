import pytest

from src.prediction.probabilities import (
    draw_probability_from_elo_diff,
    elo_win_draw_loss_probs,
)

from src.elo.expected import expected_score


def test_elo_expected_score_equal_ratings_is_half():
    assert expected_score(1500, 1500) == pytest.approx(0.5)


def test_elo_expected_score_higher_rating_is_favored():
    assert expected_score(1600, 1500) > 0.5
    assert expected_score(1500, 1600) < 0.5


def test_elo_expected_score_is_symmetric():
    prob_a = expected_score(1600, 1500)
    prob_b = expected_score(1500, 1600)

    assert prob_a + prob_b == pytest.approx(1.0)


def test_draw_probability_decreases_with_elo_gap():
    equal_draw = draw_probability_from_elo_diff(0)
    uneven_draw = draw_probability_from_elo_diff(400)

    assert equal_draw > uneven_draw


def test_draw_probability_has_minimum_floor():
    draw_prob = draw_probability_from_elo_diff(2000)

    assert draw_prob >= 0.08


def test_win_draw_loss_probabilities_sum_to_one():
    probs = elo_win_draw_loss_probs(1600, 1500)

    assert sum(probs) == pytest.approx(1.0)


def test_win_draw_loss_favors_stronger_team():
    prob_a_win, prob_draw, prob_b_win = elo_win_draw_loss_probs(1700, 1500)

    assert prob_a_win > prob_b_win
    assert prob_draw > 0