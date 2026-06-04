import pytest

from src.prediction.fixtures import build_group_stage_fixtures
from src.prediction.models import MatchFixture


def test_build_group_stage_fixtures_creates_six_matches_per_group():
    groups = {
        "A": ["Team 1", "Team 2", "Team 3", "Team 4"],
        "B": ["Team 5", "Team 6", "Team 7", "Team 8"],
    }

    fixtures = build_group_stage_fixtures(groups)

    assert len(fixtures) == 12
    assert all(isinstance(fixture, MatchFixture) for fixture in fixtures)


def test_build_group_stage_fixtures_uses_stable_readable_match_ids():
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}

    fixtures = build_group_stage_fixtures(groups)

    assert [fixture.match_id for fixture in fixtures] == [
        "group_A_1",
        "group_A_2",
        "group_A_3",
        "group_A_4",
        "group_A_5",
        "group_A_6",
    ]


def test_build_group_stage_fixtures_uses_all_pair_combinations_in_order():
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}

    fixtures = build_group_stage_fixtures(groups)

    assert [(fixture.team_a, fixture.team_b) for fixture in fixtures] == [
        ("Team 1", "Team 2"),
        ("Team 1", "Team 3"),
        ("Team 1", "Team 4"),
        ("Team 2", "Team 3"),
        ("Team 2", "Team 4"),
        ("Team 3", "Team 4"),
    ]


def test_build_group_stage_fixtures_sets_group_stage_fields():
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}

    fixture = build_group_stage_fixtures(groups)[0]

    assert fixture.stage == "group"
    assert fixture.group == "A"
    assert fixture.team_a == "Team 1"
    assert fixture.team_b == "Team 2"
    assert fixture.source_a is None
    assert fixture.source_b is None


def test_build_group_stage_fixtures_rejects_groups_without_four_teams():
    groups = {"A": ["Team 1", "Team 2", "Team 3"]}

    with pytest.raises(ValueError, match="exactly 4 teams"):
        build_group_stage_fixtures(groups)


def test_build_group_stage_fixtures_uses_configured_matches_in_stable_order():
    groups = {"A": ["Team 1", "Team 2", "Team 3", "Team 4"]}
    matches = [
        {
            "match_id": "group_A_2",
            "group": "A",
            "matchday": 2,
            "home": "Team 1",
            "away": "Team 3",
        },
        {
            "match_id": "group_A_1",
            "group": "A",
            "matchday": 1,
            "home": "Team 2",
            "away": "Team 4",
        },
    ]

    fixtures = build_group_stage_fixtures(groups, matches)

    assert [fixture.match_id for fixture in fixtures] == ["group_A_1", "group_A_2"]
    assert fixtures[0].team_a == "Team 2"
    assert fixtures[0].matchday == 1
