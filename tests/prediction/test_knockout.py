import random

import pytest

from src.prediction.tournament_flow.knockout import (
    build_knockout_fixtures,
    build_third_place_placeholder_resolution,
    rank_third_place_teams,
    resolve_knockout_fixture,
    simulate_knockout_match,
    simulate_knockout_round,
    update_knockout_elo_ratings,
)
from src.prediction.core.models import GroupOutcome, GroupStandingRow, MatchFixture, MatchResult


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


def group_outcomes_with_standings() -> dict[str, GroupOutcome]:
    return {
        "A": GroupOutcome(
            group="A",
            standings=[
                GroupStandingRow("Team 1", points=9),
                GroupStandingRow("Team 2", points=6),
                GroupStandingRow("Team 3", points=4, goals_for=5),
                GroupStandingRow("Team 4", points=0),
            ],
            winner="Team 1",
            runner_up="Team 2",
            third_place="Team 3",
        ),
        "B": GroupOutcome(
            group="B",
            standings=[
                GroupStandingRow("Team 5", points=9),
                GroupStandingRow("Team 6", points=6),
                GroupStandingRow("Team 7", points=5, goals_for=7),
                GroupStandingRow("Team 8", points=0),
            ],
            winner="Team 5",
            runner_up="Team 6",
            third_place="Team 7",
        ),
    }


def test_build_knockout_fixtures_converts_config_matches_to_source_fixtures():
    fixtures = build_knockout_fixtures(
        [{"match_id": "M73", "round": "round_of_32", "home": "2A", "away": "2B"}]
    )

    assert fixtures == [
        MatchFixture(
            match_id="M73",
            stage="round_of_32",
            team_a=None,
            team_b=None,
            source_a="2A",
            source_b="2B",
        )
    ]


def test_resolve_knockout_fixture_resolves_compact_group_placeholders():
    fixture = MatchFixture(
        match_id="M73",
        stage="round_of_32",
        team_a=None,
        team_b=None,
        source_a="1A",
        source_b="2B",
    )

    resolved = resolve_knockout_fixture(fixture, group_outcomes())

    assert resolved.team_a == "Team 1"
    assert resolved.team_b == "Team 4"


def test_resolve_knockout_fixture_resolves_winner_and_runner_up_match_placeholders():
    fixture = MatchFixture(
        match_id="M103",
        stage="third_place_playoff",
        team_a=None,
        team_b=None,
        source_a="W73",
        source_b="RU74",
    )
    match_results = {
        "M73": MatchResult("Team 1", "Team 2", 2, 1, "Team 1", False, "regular_time", "M73"),
        "M74": MatchResult("Team 3", "Team 4", 0, 1, "Team 4", False, "regular_time", "M74"),
    }

    resolved = resolve_knockout_fixture(
        fixture,
        group_outcomes(),
        match_results=match_results,
    )

    assert resolved.team_a == "Team 1"
    assert resolved.team_b == "Team 3"


def test_resolve_knockout_fixture_resolves_best_third_from_allowed_groups():
    fixture = MatchFixture(
        match_id="M74",
        stage="round_of_32",
        team_a="Team 9",
        team_b=None,
        source_b="3AB",
    )
    used_third_place_groups: set[str] = set()

    resolved = resolve_knockout_fixture(
        fixture,
        group_outcomes_with_standings(),
        third_place_rankings=rank_third_place_teams(group_outcomes_with_standings()),
        used_third_place_groups=used_third_place_groups,
    )

    assert resolved.team_b == "Team 7"
    assert used_third_place_groups == {"B"}


def test_resolve_knockout_fixture_resolves_third_place_from_combination_table():
    fixture = MatchFixture(
        match_id="M74",
        stage="round_of_32",
        team_a="Team 9",
        team_b=None,
        source_b="3AB",
    )
    used_third_place_groups: set[str] = set()

    resolved = resolve_knockout_fixture(
        fixture,
        group_outcomes_with_standings(),
        third_place_rankings=rank_third_place_teams(group_outcomes_with_standings()),
        used_third_place_groups=used_third_place_groups,
        third_place_placeholder_resolution={"3AB": "3A"},
    )

    assert resolved.team_b == "Team 3"
    assert used_third_place_groups == {"A"}


def test_build_third_place_placeholder_resolution_uses_top_eight_group_key():
    rankings = [
        (group, GroupStandingRow(f"Team {group}", points=12 - index))
        for index, group in enumerate("ABCDEFGHI")
    ]

    resolution = build_third_place_placeholder_resolution(
        rankings,
        {"ABCDEFGH": {"3ABCDF": "3A"}},
    )

    assert resolution == {"3ABCDF": "3A"}


def test_resolve_knockout_fixture_keeps_already_resolved_teams_and_metadata():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        group=None,
        team_a="Team 1",
        team_b="Team 2",
        source_a="1A",
        source_b="2B",
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
    assert resolved.source_a == "1A"
    assert resolved.source_b == "2B"


def test_resolve_knockout_fixture_rejects_invalid_placeholder():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a=None,
        team_b="Team 2",
        source_a="invalid_placeholder",
    )

    with pytest.raises(ValueError, match="Invalid knockout placeholder"):
        resolve_knockout_fixture(fixture, group_outcomes())


def test_resolve_knockout_fixture_rejects_unknown_group():
    fixture = MatchFixture(
        match_id="knockout_1",
        stage="round_of_32",
        team_a=None,
        team_b="Team 2",
        source_a="1Z",
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
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", lambda lambda_, max_goals=10, rng=None: 1)

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


def test_update_knockout_elo_ratings_rewards_winner_and_penalizes_loser():
    fixture = MatchFixture("M1", "round_of_16", "Team 1", "Team 2")
    result = MatchResult("Team 1", "Team 2", 2, 0, "Team 1", False, "regular_time", "M1")
    ratings = {"Team 1": 1500.0, "Team 2": 1500.0}

    update_knockout_elo_ratings(ratings, fixture, result)

    assert ratings["Team 1"] > 1500.0
    assert ratings["Team 2"] < 1500.0


def test_update_knockout_elo_ratings_uses_same_k_factor_across_world_cup_stages():
    round_of_16_ratings = {"Team 1": 1500.0, "Team 2": 1500.0}
    quarter_final_ratings = round_of_16_ratings.copy()
    result = MatchResult("Team 1", "Team 2", 1, 0, "Team 1", False, "regular_time", "M1")

    update_knockout_elo_ratings(
        round_of_16_ratings,
        MatchFixture("M1", "round_of_16", "Team 1", "Team 2"),
        result,
    )
    update_knockout_elo_ratings(
        quarter_final_ratings,
        MatchFixture("M1", "quarter_final", "Team 1", "Team 2"),
        result,
    )

    assert quarter_final_ratings == round_of_16_ratings
