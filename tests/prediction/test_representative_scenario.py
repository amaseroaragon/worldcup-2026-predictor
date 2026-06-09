from src.prediction.tournament_flow.bracket_predictions import (
    build_predicted_bracket_predictions,
)
from src.prediction.tournament_flow.monte_carlo import run_monte_carlo
from src.prediction.tournament_flow.representative_scenario import (
    representative_outcome_distance,
    select_representative_outcome,
)

from tests.prediction.test_monte_carlo import (
    mini_groups,
    mini_knockout_matches,
    mini_ratings,
)


def test_select_representative_outcome_minimizes_aggregate_distance():
    groups = mini_groups()
    _probabilities, outcomes = run_monte_carlo(
        groups,
        mini_ratings(groups),
        mini_knockout_matches(),
        simulations=20,
        seed=42,
        return_outcomes=True,
    )

    selected = select_representative_outcome(outcomes, groups)
    selected_distance = representative_outcome_distance(selected, outcomes, groups)

    assert selected in outcomes
    assert selected_distance == min(
        representative_outcome_distance(outcome, outcomes, groups)
        for outcome in outcomes
    )


def test_representative_predictions_use_one_complete_simulated_outcome():
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
    selected = select_representative_outcome(outcomes, groups)
    selected_results = {
        result.match_id: result
        for result in selected.match_results
    }

    predictions = build_predicted_bracket_predictions(
        outcomes,
        groups,
        ratings,
        knockout_matches,
        representative_outcome=selected,
    )

    for prediction in predictions:
        result = selected_results[prediction.match_id]
        assert prediction.home_team == result.team_a
        assert prediction.away_team == result.team_b
        assert prediction.predicted_home_goals == result.goals_a
        assert prediction.predicted_away_goals == result.goals_b
        assert prediction.predicted_winner == result.winner
        assert prediction.source == "representative_monte_carlo_outcome"
