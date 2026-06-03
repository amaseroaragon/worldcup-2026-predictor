import random

import pytest

from src.prediction.knockout import resolve_knockout_fixture, simulate_knockout_match, simulate_knockout_round
from src.prediction.models import GroupOutcome, MatchFixture, MatchResult


def knockout_fixture() -> MatchFixture:
    return MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a="Team 1",
        team_b="Team 2",
    )


def group_outcomes() -> dict[str, GroupOutcome]:
    return {
        "A": GroupOutcome(group="A", standings=[], winner="Team 1", runner_up="Team 2"),
        "B": GroupOutcome(group="B", standings=[], winner="Team 3", runner_up="Team 4"),
    }


def test_resolve_knockout_fixture_resolves_winner_group_placeholder():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a=None,
        team_b="Team 4",
        source_a="winner_group_A",
    )

    resolved = resolve_knockout_fixture(fixture, group_outcomes())

    assert resolved.team_a == "Team 1"
    assert resolved.team_b == "Team 4"
    assert fixture.team_a is None


def test_resolve_knockout_fixture_resolves_runner_up_group_placeholder():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a="Team 1",
        team_b=None,
        source_b="runner_up_group_B",
    )

    resolved = resolve_knockout_fixture(fixture, group_outcomes())

    assert resolved.team_a == "Team 1"
    assert resolved.team_b == "Team 4"


def test_resolve_knockout_fixture_keeps_already_resolved_teams_and_metadata():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        group=None,
        team_a="Team 1",
        team_b="Team 2",
        source_a="winner_group_A",
        source_b="runner_up_group_B",
        date="2026-07-01",
    )

    resolved = resolve_knockout_fixture(fixture, group_outcomes())

    assert resolved is not fixture
    assert resolved.match_id == fixture.match_id
    assert resolved.stage == fixture.stage
    assert resolved.group == fixture.group
    assert resolved.date == fixture.date
    assert resolved.team_a == "Team 1"
    assert resolved.team_b == "Team 2"
    assert resolved.source_a == "winner_group_A"
    assert resolved.source_b == "runner_up_group_B"


def test_resolve_knockout_fixture_rejects_invalid_placeholder():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a=None,
        team_b="Team 2",
        source_a="third_place_group_A",
    )

    with pytest.raises(ValueError, match="Invalid knockout placeholder"):
        resolve_knockout_fixture(fixture, group_outcomes())


def test_resolve_knockout_fixture_rejects_unknown_group():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a=None,
        team_b="Team 2",
        source_a="winner_group_Z",
    )

    with pytest.raises(ValueError, match="Unknown group"):
        resolve_knockout_fixture(fixture, group_outcomes())


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


def test_simulate_knockout_round_simulates_multiple_matches():
    fixtures = [
        MatchFixture("knockout_1", "round_of_32", "Team 1", "Team 2"),
        MatchFixture("knockout_2", "round_of_32", "Team 3", "Team 4"),
    ]
    ratings = {
        "Team 1": 1600.0,
        "Team 2": 1550.0,
        "Team 3": 1500.0,
        "Team 4": 1650.0,
    }

    results, winners = simulate_knockout_round(fixtures, ratings, rng=random.Random(42))

    assert len(results) == len(fixtures)
    assert len(winners) == len(fixtures)
    assert all(isinstance(result, MatchResult) for result in results)


def test_simulate_knockout_round_returns_winners_in_fixture_order():
    fixtures = [
        MatchFixture("knockout_1", "round_of_32", "Team 1", "Team 2"),
        MatchFixture("knockout_2", "round_of_32", "Team 3", "Team 4"),
    ]
    ratings = {
        "Team 1": 1800.0,
        "Team 2": 1200.0,
        "Team 3": 1800.0,
        "Team 4": 1200.0,
    }

    results, winners = simulate_knockout_round(fixtures, ratings, rng=random.Random(42))

    assert winners == [result.winner for result in results]
    assert all(winner is not None for winner in winners)


def test_simulate_knockout_round_rejects_empty_fixture_list():
    with pytest.raises(ValueError, match="at least one fixture"):
        simulate_knockout_round([], {})
