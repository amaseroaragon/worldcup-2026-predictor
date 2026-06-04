import random

import pytest

from src.prediction.models import MatchResult
from src.prediction.fixtures import build_group_stage_fixtures
from src.prediction.group_stage import simulate_group_stage
from src.prediction.models import MatchFixture


def test_group_stage_flow_builds_fixtures_and_simulates_groups():
    groups = {
        "A": ["Team 1", "Team 2", "Team 3", "Team 4"],
        "B": ["Team 5", "Team 6", "Team 7", "Team 8"],
    }
    ratings = {team: 1600.0 for teams in groups.values() for team in teams}

    fixtures = build_group_stage_fixtures(groups)
    outcomes = simulate_group_stage(fixtures, ratings, rng=random.Random(42))

    assert len(fixtures) == 12
    assert len(outcomes) == 2

    for group, outcome in outcomes.items():
        group_teams = set(groups[group])

        assert outcome.group == group
        assert len(outcome.match_results) == 6
        assert len(outcome.standings) == 4
        assert outcome.winner in group_teams
        assert outcome.runner_up in group_teams
        assert outcome.third_place in group_teams
        assert {row.team for row in outcome.standings} == group_teams


def test_simulate_group_stage_accepts_optional_rng():
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}
    fixtures = build_group_stage_fixtures(groups)
    ratings = {team: 1600.0 for team in groups["A"]}

    outcomes = simulate_group_stage(fixtures, ratings)

    assert set(outcomes) == {"A"}


def test_simulate_group_stage_rejects_fixture_without_group():
    fixture = MatchFixture(
        match_id="missing_group",
        stage="group",
        team_a="Team 1",
        team_b="Team 2",
    )

    with pytest.raises(ValueError, match="missing a group"):
        simulate_group_stage([fixture], {"Team 1": 1600.0, "Team 2": 1600.0})


def test_simulate_group_stage_rejects_missing_elo_rating():
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}
    fixtures = build_group_stage_fixtures(groups)
    ratings = {"Team 1": 1600.0, "Team 2": 1600.0, "Team 3": 1600.0}

    with pytest.raises(ValueError, match="Missing Elo rating"):
        simulate_group_stage(fixtures, ratings)


def test_simulate_group_stage_rejects_incomplete_group():
    fixtures = build_group_stage_fixtures({"A": ["Team 1", "Team 2", "Team 3", "Team 4"]})[:-1]
    ratings = {
        "Team 1": 1600.0,
        "Team 2": 1600.0,
        "Team 3": 1600.0,
        "Team 4": 1600.0,
    }

    with pytest.raises(ValueError, match="4 teams and 6 fixtures"):
        simulate_group_stage(fixtures, ratings)


def test_simulate_group_stage_rejects_non_group_stage_fixture():
    fixture = MatchFixture(
        match_id="R32_1",
        stage="round_of_32",
        group="A",
        team_a="Team 1",
        team_b="Team 2",
    )

    with pytest.raises(ValueError, match="stage='group'"):
        simulate_group_stage([fixture], {"Team 1": 1600.0, "Team 2": 1600.0})


def test_simulate_group_stage_updates_elo_and_uses_it_in_later_matches(monkeypatch):
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}
    fixtures = build_group_stage_fixtures(groups)
    ratings = {team: 1500.0 for team in groups["A"]}
    observed_team_1_ratings = []
    observed_team_2_ratings = []

    def fake_simulate_match(fixture, ratings, **kwargs):
        if fixture.team_a == "Team 1":
            observed_team_1_ratings.append(ratings["Team 1"])
        if "Team 2" in {fixture.team_a, fixture.team_b}:
            observed_team_2_ratings.append(ratings["Team 2"])
        return MatchResult(
            fixture.team_a,
            fixture.team_b,
            1,
            0,
            fixture.team_a,
            False,
            "regular_time",
            fixture.match_id,
        )

    monkeypatch.setattr("src.prediction.group_stage.simulate_match", fake_simulate_match)

    simulate_group_stage(fixtures, ratings)

    assert ratings["Team 1"] > 1500.0
    assert observed_team_1_ratings[1] > observed_team_1_ratings[0]
    assert observed_team_2_ratings[1] < observed_team_2_ratings[0]


def test_simulate_group_stage_fixed_elo_preserves_ratings(monkeypatch):
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}
    fixtures = build_group_stage_fixtures(groups)
    ratings = {team: 1500.0 for team in groups["A"]}
    original_ratings = ratings.copy()

    monkeypatch.setattr("src.prediction.config.USE_DYNAMIC_ELO_GROUP_STAGE", False)

    simulate_group_stage(fixtures, ratings, rng=random.Random(42))

    assert ratings == original_ratings
