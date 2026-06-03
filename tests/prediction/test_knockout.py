import random

import pytest

from src.prediction.knockout import simulate_knockout_match
from src.prediction.models import MatchFixture, MatchResult


def knockout_fixture() -> MatchFixture:
    return MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a="Team 1",
        team_b="Team 2",
    )


def test_simulate_knockout_match_returns_match_result():
    result = simulate_knockout_match(
        fixture=knockout_fixture(),
        ratings={"Team 1": 1600.0, "Team 2": 1550.0},
        rng=random.Random(42),
    )

    assert isinstance(result, MatchResult)
    assert result.match_id == "knockout_1"


def test_simulate_knockout_match_always_returns_winner():
    result = simulate_knockout_match(
        fixture=knockout_fixture(),
        ratings={"Team 1": 1600.0, "Team 2": 1550.0},
        rng=random.Random(42),
    )

    assert result.winner in {"Team 1", "Team 2"}
    assert result.is_draw is False


def test_simulate_knockout_match_rejects_group_fixture():
    fixture = MatchFixture(
        match_id="group_A_1",
        stage="group",
        group="A",
        team_a="Team 1",
        team_b="Team 2",
    )

    with pytest.raises(ValueError, match="stage='group'"):
        simulate_knockout_match(fixture, {"Team 1": 1600.0, "Team 2": 1550.0})


def test_simulate_knockout_match_rejects_fixture_without_team_a_or_team_b():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a=None,
        team_b="Team 2",
    )

    with pytest.raises(ValueError, match="both teams defined"):
        simulate_knockout_match(fixture, {"Team 2": 1550.0})


def test_simulate_knockout_match_rejects_missing_elo_rating():
    with pytest.raises(ValueError, match="Missing Elo rating"):
        simulate_knockout_match(knockout_fixture(), {"Team 1": 1600.0})


def test_simulate_knockout_match_uses_injected_rng_for_tiebreaker(monkeypatch):
    monkeypatch.setattr("src.prediction.match.sample_poisson", lambda lambda_, max_goals=10, rng=None: 1)

    ratings = {"Team 1": 1600.0, "Team 2": 1600.0}

    result_a = simulate_knockout_match(knockout_fixture(), ratings, rng=random.Random(1))
    result_b = simulate_knockout_match(knockout_fixture(), ratings, rng=random.Random(2))

    assert result_a.decided_by == "tiebreaker"
    assert result_b.decided_by == "tiebreaker"
    assert result_a.winner == "Team 1"
    assert result_b.winner == "Team 2"
