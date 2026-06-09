from src.prediction.tournament_flow.bracket_predictions import (
    build_displayed_group_outcomes,
    build_predicted_bracket_predictions,
)
from src.prediction.tournament_flow.monte_carlo import run_monte_carlo
from src.prediction.tournament_flow.prediction_summary import select_most_probable_outcome

from tests.prediction.test_monte_carlo import (
    mini_groups,
    mini_knockout_matches,
    mini_ratings,
)

def test_displayed_predictions_use_each_match_most_probable_outcome():
    groups = mini_groups()
    ratings = mini_ratings(groups)
    knockout_matches = mini_knockout_matches()
    _probabilities, outcomes = run_monte_carlo(
        groups,
        ratings,
        knockout_matches,
        simulations=20,
        seed=42,
        return_outcomes=True,
    )
    predictions = build_predicted_bracket_predictions(
        outcomes,
        groups,
        ratings,
        knockout_matches,
    )

    for prediction in predictions:
        displayed_outcome = (
            "home_win"
            if prediction.predicted_home_goals > prediction.predicted_away_goals
            else "away_win"
            if prediction.predicted_away_goals > prediction.predicted_home_goals
            else "draw"
        )
        assert displayed_outcome == select_most_probable_outcome(
            prediction.home_win_probability,
            prediction.draw_probability,
            prediction.away_win_probability,
        )
        assert prediction.source in {"most_probable_outcome", "direct_model_fallback"}

    displayed_groups = build_displayed_group_outcomes(
        [prediction for prediction in predictions if prediction.stage == "group"]
    )
    assert set(displayed_groups) == set(groups)
