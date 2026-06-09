from unittest.mock import patch

import pytest

from src.prediction.core.models import MatchResult
from src.prediction.core.poisson import expected_goals_from_elo, score_matrix
from src.prediction.tournament_flow.bracket_predictions import (
    _prediction_from_direct_model,
    _prediction_from_results,
)
from src.prediction.tournament_flow.prediction_summary import (
    AWAY_WIN,
    DRAW,
    HOME_WIN,
    select_most_likely_score_for_outcome,
    select_most_probable_outcome,
)


RESULTS = [
    MatchResult("Home", "Away", 1, 0, "Home", False, "regular_time", "M1"),
]


def build_prediction(
    probabilities: tuple[float, float, float],
    *,
    knockout: bool = False,
):
    with patch(
        "src.prediction.tournament_flow.bracket_predictions.result_probabilities",
        return_value=probabilities,
    ):
        return _prediction_from_results(
            match_id="M1" if knockout else "group_A_1",
            stage="round_of_32" if knockout else "group",
            group=None if knockout else "A",
            round_name="round_of_32" if knockout else None,
            home_team="Home",
            away_team="Away",
            results=RESULTS,
            ratings={"Home": 1600.0, "Away": 1500.0},
            simulations_count=10,
            appearance_count=10,
            source="test",
            knockout=knockout,
        )


def test_highest_home_win_probability_selects_home_win_score_and_winner():
    prediction = build_prediction((0.60, 0.20, 0.20))

    assert prediction.predicted_home_goals > prediction.predicted_away_goals
    assert prediction.predicted_winner == "Home"
    assert prediction.advanced_by is None


def test_highest_away_win_probability_selects_away_win_score_and_winner():
    prediction = build_prediction((0.20, 0.20, 0.60))

    assert prediction.predicted_away_goals > prediction.predicted_home_goals
    assert prediction.predicted_winner == "Away"
    assert prediction.advanced_by is None


def test_highest_draw_probability_selects_group_draw_without_winner():
    prediction = build_prediction((0.25, 0.50, 0.25))

    assert prediction.predicted_home_goals == prediction.predicted_away_goals
    assert prediction.predicted_winner is None
    assert prediction.advanced_by is None


def test_highest_draw_probability_selects_knockout_draw_with_winner():
    prediction = build_prediction((0.30, 0.50, 0.20), knockout=True)

    assert prediction.predicted_home_goals == prediction.predicted_away_goals
    assert prediction.predicted_winner == "Home"
    assert prediction.advanced_by == "higher_win_probability_after_draw"


def test_direct_knockout_prediction_has_non_null_winner():
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
    )

    assert prediction.draw_probability > 0
    assert prediction.predicted_winner is not None


@pytest.mark.parametrize(
    ("probabilities", "outcome"),
    [
        ((0.60, 0.20, 0.20), HOME_WIN),
        ((0.20, 0.60, 0.20), DRAW),
        ((0.20, 0.20, 0.60), AWAY_WIN),
    ],
)
def test_select_most_probable_outcome(probabilities, outcome):
    assert select_most_probable_outcome(*probabilities) == outcome


@pytest.mark.parametrize(
    ("outcome", "expected_score"),
    [
        (HOME_WIN, (1, 0)),
        (DRAW, (0, 0)),
        (AWAY_WIN, (0, 1)),
    ],
)
def test_select_most_likely_score_for_outcome_never_contradicts_outcome(
    outcome,
    expected_score,
):
    matrix = [
        [0.30, 0.20, 0.05],
        [0.25, 0.10, 0.04],
        [0.03, 0.02, 0.01],
    ]

    assert select_most_likely_score_for_outcome(matrix, outcome) == expected_score


def test_score_selection_does_not_change_lambdas():
    lambdas_before = expected_goals_from_elo(1600.0, 1500.0)
    matrix = score_matrix(*lambdas_before)

    outcome = select_most_probable_outcome(0.45, 0.25, 0.30)
    select_most_likely_score_for_outcome(matrix, outcome)

    assert expected_goals_from_elo(1600.0, 1500.0) == lambdas_before
