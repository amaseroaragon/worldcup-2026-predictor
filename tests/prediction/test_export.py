import json

import pandas as pd
import pytest

from src.prediction.export import (
    PROBABILITY_COLUMNS,
    build_match_predictions,
    build_predicted_bracket_predictions,
    export_match_predictions_json,
    export_probabilities,
    probabilities_to_dataframe,
    validate_probability_output,
)
from src.prediction.models import MatchPrediction, MatchResult
from src.prediction.tournament import simulate_tournament_once


def sample_probabilities() -> dict:
    return {
        "Team 1": {"champion": 0.2, "runner_up": 0.3, "semifinal": 0.5},
        "Team 2": {"champion": 0.8, "runner_up": 0.1, "semifinal": 0.9},
    }


def test_probabilities_to_dataframe_returns_expected_columns_sorted_by_champion_probability():
    df = probabilities_to_dataframe(sample_probabilities())

    assert df.columns.tolist() == PROBABILITY_COLUMNS
    assert df["team"].tolist() == ["Team 2", "Team 1"]


def test_probabilities_to_dataframe_exports_float_probabilities_between_zero_and_one():
    df = probabilities_to_dataframe(sample_probabilities())

    for column in ["champion_probability", "runner_up_probability", "semifinal_probability"]:
        assert pd.api.types.is_float_dtype(df[column])
        assert df[column].between(0, 1).all()


def test_export_probabilities_writes_csv(tmp_path):
    output_path = tmp_path / "world_cup_probabilities.csv"

    df = export_probabilities(sample_probabilities(), output_path)
    written = pd.read_csv(output_path)

    assert output_path.exists()
    assert written.columns.tolist() == PROBABILITY_COLUMNS
    assert written["team"].tolist() == df["team"].tolist()


def test_build_match_predictions_returns_prediction_records():
    results = [
        MatchResult(
            team_a="Team 1",
            team_b="Team 2",
            goals_a=2,
            goals_b=1,
            winner="Team 1",
            is_draw=False,
            decided_by="regular_time",
            match_id="group_A_1",
        )
    ]
    ratings = {"Team 1": 1600.0, "Team 2": 1500.0}

    predictions = build_match_predictions(results, ratings)

    assert len(predictions) == 1
    prediction = predictions[0]
    assert isinstance(prediction, MatchPrediction)
    assert prediction.match_id == "group_A_1"
    assert prediction.stage == "group"
    assert prediction.group == "A"
    assert prediction.round is None
    assert prediction.home_team == "Team 1"
    assert prediction.away_team == "Team 2"
    assert prediction.predicted_home_goals == 2
    assert prediction.predicted_away_goals == 1
    assert prediction.predicted_winner == "Team 1"
    assert prediction.user_home_goals is None
    assert prediction.user_away_goals is None
    assert prediction.real_home_goals is None
    assert prediction.real_away_goals is None
    assert prediction.prediction_correct is None


def test_build_match_predictions_includes_knockout_round_metadata():
    results = [
        MatchResult(
            team_a="Team 1",
            team_b="Team 2",
            goals_a=1,
            goals_b=1,
            winner="Team 2",
            is_draw=False,
            decided_by="tiebreaker",
            match_id="M73",
        )
    ]
    ratings = {"Team 1": 1600.0, "Team 2": 1500.0}
    knockout_matches = [
        {"match_id": "M73", "round": "round_of_32", "home": "1A", "away": "2B"}
    ]

    predictions = build_match_predictions(results, ratings, knockout_matches)

    assert predictions[0].stage == "round_of_32"
    assert predictions[0].round == "round_of_32"
    assert predictions[0].group is None


def test_export_match_predictions_json_writes_structured_file(tmp_path):
    output_path = tmp_path / "tournament_predictions.json"
    predictions = [
        MatchPrediction(
            match_id="group_A_1",
            stage="group",
            group="A",
            round=None,
            home_team="Team 1",
            away_team="Team 2",
            predicted_home_goals=2,
            predicted_away_goals=1,
            predicted_winner="Team 1",
            home_win_probability=0.5,
            draw_probability=0.25,
            away_win_probability=0.25,
        )
    ]

    payload = export_match_predictions_json(
        predictions,
        output_path,
        metadata={"simulations": 10},
    )

    with output_path.open(encoding="utf-8") as file:
        written = json.load(file)

    assert output_path.exists()
    assert payload == written
    assert written["metadata"]["simulations"] == 10
    assert written["matches"][0]["user_home_goals"] is None
    assert written["matches"][0]["real_home_goals"] is None
    assert written["matches"][0]["prediction_correct"] is None


def test_build_predicted_bracket_predictions_returns_one_entry_per_bracket_slot():
    groups = {
        "A": ["Team 1", "Team 2", "Team 3", "Team 4"],
        "B": ["Team 5", "Team 6", "Team 7", "Team 8"],
        "C": ["Team 9", "Team 10", "Team 11", "Team 12"],
        "D": ["Team 13", "Team 14", "Team 15", "Team 16"],
    }
    ratings = {
        team: 1800.0 - index * 20
        for index, team in enumerate(team for teams in groups.values() for team in teams)
    }
    knockout_matches = [
        {"match_id": "M1", "round": "quarter_final", "home": "1A", "away": "2B"},
        {"match_id": "M2", "round": "quarter_final", "home": "1B", "away": "2A"},
        {"match_id": "M3", "round": "quarter_final", "home": "1C", "away": "2D"},
        {"match_id": "M4", "round": "quarter_final", "home": "1D", "away": "2C"},
        {"match_id": "M5", "round": "semi_final", "home": "W1", "away": "W2"},
        {"match_id": "M6", "round": "semi_final", "home": "W3", "away": "W4"},
        {"match_id": "M7", "round": "final", "home": "W5", "away": "W6"},
    ]
    outcomes = [
        simulate_tournament_once(
            groups=groups,
            ratings=ratings,
            knockout_matches=knockout_matches,
        )
        for _ in range(5)
    ]

    predictions = build_predicted_bracket_predictions(
        outcomes,
        groups,
        ratings,
        knockout_matches,
    )

    assert len(predictions) == 31
    assert len({prediction.match_id for prediction in predictions}) == 31
    assert predictions[-1].round == "final"


def test_validate_probability_output_accepts_valid_output():
    df = probabilities_to_dataframe(sample_probabilities())

    validate_probability_output(df)


def test_validate_probability_output_rejects_missing_columns():
    df = pd.DataFrame({"team": ["Team 1"]})

    with pytest.raises(ValueError, match="Missing probability output columns"):
        validate_probability_output(df)


def test_validate_probability_output_rejects_probabilities_outside_range():
    df = probabilities_to_dataframe(sample_probabilities())
    df.loc[0, "champion_probability"] = 1.2

    with pytest.raises(ValueError, match="between 0 and 1"):
        validate_probability_output(df)
