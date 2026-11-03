import json
from pathlib import Path

import pytest

from src.evaluation.world_cup_2026 import (
    ActualMatch,
    _validate_knockout_progression,
    actual_stage_reached,
    evaluate_forecast,
    read_actual_matches,
)

ROOT = Path(__file__).resolve().parents[2]
PREDICTIONS = ROOT / "outputs" / "predictions"


def match(number, stage, home, away, home_score, away_score, winner=None, shootout=None, group=None):
    return ActualMatch(number, "2026-07-01", stage, group, home, away, home_score, away_score, shootout, winner)


def load(name):
    return json.loads((PREDICTIONS / name).read_text(encoding="utf-8"))


def test_actual_results_file_is_a_complete_consistent_tournament():
    matches = read_actual_matches(ROOT / "data" / "actual" / "world_cup_2026_results.csv")

    assert len(matches) == 104
    assert sum(m.stage == "group" for m in matches) == 72
    _validate_knockout_progression(matches)
    assert all(m.winner for m in matches if m.stage != "group")


def test_actual_stage_reached_uses_furthest_round_and_final_winner():
    matches = [
        match(1, "semi_final", "A", "B", 1, 0, winner="A"),
        match(2, "semi_final", "C", "D", 1, 1, winner="D", shootout="D"),
        match(3, "third_place_playoff", "B", "C", 2, 0, winner="B"),
        match(4, "final", "A", "D", 0, 1, winner="D"),
    ]

    assert actual_stage_reached(matches) == {
        "A": "final",
        "B": "semi_final",
        "C": "semi_final",
        "D": "champion",
    }


def test_knockout_progression_rejects_teams_that_did_not_advance():
    matches = [
        match(1, "round_of_32", "A", "B", 1, 0, winner="A"),
        match(2, "round_of_16", "B", "C", 1, 0, winner="B"),
    ]

    with pytest.raises((ValueError, KeyError)):
        _validate_knockout_progression(matches)


def test_evaluate_forecast_aligns_swapped_home_and_away():
    predictions = load("tournament_predictions.json")
    first = next(m for m in predictions["matches"] if m["stage"] == "group")
    actual = read_actual_matches(ROOT / "data" / "actual" / "world_cup_2026_results.csv")
    flipped = [
        ActualMatch(
            m.match_number, m.date, m.stage, m.group, m.away_team, m.home_team,
            m.away_score, m.home_score, m.shootout_winner, m.winner,
        )
        if {m.home_team, m.away_team} == {first["home_team"], first["away_team"]}
        else m
        for m in actual
    ]

    report = evaluate_forecast(
        flipped,
        predictions,
        load("world_cup_probabilities.json"),
        load("group_results.json"),
        load("representative_tournament.json"),
    )
    row = next(r for r in report["group_stage"]["matches"] if r["home_team"] == first["away_team"])

    assert row["home_win_probability"] == first["away_win_probability"]
    assert row["away_win_probability"] == first["home_win_probability"]


def test_evaluate_forecast_report_shape():
    report = evaluate_forecast(
        read_actual_matches(ROOT / "data" / "actual" / "world_cup_2026_results.csv"),
        load("tournament_predictions.json"),
        load("world_cup_probabilities.json"),
        load("group_results.json"),
        load("representative_tournament.json"),
    )

    assert report["group_stage"]["summary"]["matches"] == 72
    assert len(report["knockout_matches"]) == 32
    assert len(report["teams"]) == 48
    for row in report["group_stage"]["matches"]:
        total = row["home_win_probability"] + row["draw_probability"] + row["away_win_probability"]
        assert total == pytest.approx(1, abs=1e-3)


def test_exact_match_probabilities_agree_with_the_simulation():
    from src.evaluation.match_probabilities import match_probabilities
    from src.prediction.pipeline import load_prediction_inputs

    inputs = load_prediction_inputs()
    # Opening match: no in-tournament Elo updates yet, so the 10,000-run frequencies are comparable.
    simulated = next(m for m in load("tournament_predictions.json")["matches"] if m["match_id"] == "group_A_1")
    exact = match_probabilities(simulated["home_team"], simulated["away_team"], inputs)

    assert exact.win_a + exact.draw + exact.win_b == pytest.approx(1)
    assert exact.win_a == pytest.approx(simulated["home_win_probability"], abs=0.015)
    assert exact.draw == pytest.approx(simulated["draw_probability"], abs=0.015)
    assert exact.win_a <= exact.advance_a <= exact.win_a + exact.draw


def test_evaluate_forecast_scores_knockouts_when_probabilities_are_given():
    from src.evaluation.match_probabilities import MatchProbabilities

    actual = read_actual_matches(ROOT / "data" / "actual" / "world_cup_2026_results.csv")
    even = MatchProbabilities(1.2, 1.2, 0.4, 0.2, 0.4, 0.6)
    report = evaluate_forecast(
        actual,
        load("tournament_predictions.json"),
        load("world_cup_probabilities.json"),
        load("group_results.json"),
        load("representative_tournament.json"),
        {m.match_number: even for m in actual if m.stage != "group"},
    )

    summary = report["knockout_summary"]
    assert summary["matches"] == 32
    home_wins = sum(m.winner == m.home_team for m in actual if m.stage != "group")
    assert summary["favourite_advanced"] == home_wins
    assert all(row["model_favourite"] == row["home_team"] for row in report["knockout_matches"])
