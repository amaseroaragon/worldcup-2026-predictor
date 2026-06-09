from unittest.mock import patch

import pytest

from src.prediction.core.models import MatchResult
from src.prediction.core.poisson import expected_goals_from_elo, score_matrix
from src.prediction.tournament_flow.bracket_predictions import (
    _prediction_from_direct_model,
    _prediction_from_results,
)
from src.prediction.tournament_flow.prediction_summary import (
    result_probabilities,
    select_representative_score,
)


def _results() -> list[MatchResult]:
    return [
        MatchResult("Home", "Away", 1, 0, "Home", False, "regular_time", "M1"),
        MatchResult("Home", "Away", 1, 1, "Home", False, "tiebreaker", "M1"),
        MatchResult("Home", "Away", 0, 1, "Away", False, "regular_time", "M1"),
        MatchResult("Home", "Away", 2, 2, "Away", False, "tiebreaker", "M1"),
        MatchResult("Home", "Away", 2, 0, "Home", False, "regular_time", "M1"),
    ]


def test_group_draw_representative_score_has_no_winner():
    with patch(
        "src.prediction.tournament_flow.bracket_predictions.select_representative_score",
        return_value=(1, 1),
    ):
        prediction = _prediction_from_results(
            match_id="group_A_1",
            stage="group",
            group="A",
            round_name=None,
            home_team="Home",
            away_team="Away",
            results=_results(),
            ratings={"Home": 1600.0, "Away": 1500.0},
            simulations_count=5,
            appearance_count=5,
            source="test",
        )

    assert prediction.predicted_winner is None
    assert prediction.advanced_by is None


def test_knockout_draw_advances_team_with_higher_win_probability():
    with patch(
        "src.prediction.tournament_flow.bracket_predictions.select_representative_score",
        return_value=(1, 1),
    ):
        prediction = _prediction_from_results(
            match_id="M1",
            stage="round_of_32",
            group=None,
            round_name="round_of_32",
            home_team="Home",
            away_team="Away",
            results=_results(),
            ratings={"Home": 1600.0, "Away": 1500.0},
            simulations_count=5,
            appearance_count=5,
            source="test",
            knockout=True,
        )

    assert prediction.home_win_probability > prediction.away_win_probability
    assert prediction.predicted_winner == "Home"
    assert prediction.advanced_by == "higher_win_probability_after_draw"


def test_knockout_probabilities_keep_draws_from_90_minutes():
    home_win, draw, away_win = result_probabilities(
        _results(),
        "Home",
        "Away",
        knockout=True,
    )

    assert (home_win, draw, away_win) == pytest.approx((0.4, 0.4, 0.2))
    assert home_win + draw + away_win == pytest.approx(1.0)


def test_direct_knockout_prediction_does_not_force_draw_probability_to_zero():
    prediction = _prediction_from_direct_model(
        match_id="M1",
        stage="round_of_32",
        round_name="round_of_32",
        home_team="Home",
        away_team="Away",
        ratings={"Home": 1600.0, "Away": 1500.0},
        simulations_count=10,
        team_strength_ratings=None,
        recent_form_ratings=None,
        squad_strength_ratings=None,
        representative_score_seed=42,
    )

    assert prediction.draw_probability > 0
    assert prediction.predicted_winner is not None


def test_select_representative_score_is_deterministic_with_seed():
    matrix = score_matrix(1.56, 1.12)

    first = select_representative_score(matrix, 0.45, 0.25, 0.30, seed=42)
    second = select_representative_score(matrix, 0.45, 0.25, 0.30, seed=42)

    assert first == second


def test_select_representative_score_does_not_change_lambdas():
    lambdas_before = expected_goals_from_elo(1600.0, 1500.0)
    matrix = score_matrix(*lambdas_before)

    select_representative_score(matrix, 0.45, 0.25, 0.30, seed=42)
    lambdas_after = expected_goals_from_elo(1600.0, 1500.0)

    assert lambdas_after == lambdas_before
