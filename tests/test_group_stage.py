import random

from src.prediction.group_stage import simulate_group_stage
from src.prediction.models import MatchFixture, SimulationConfig


def test_simulate_group_stage_returns_group_outcome_for_four_team_group():
    fixtures = [
        MatchFixture("A1", "group", "Spain", "France", group="A"),
        MatchFixture("A2", "group", "Brazil", "Japan", group="A"),
        MatchFixture("A3", "group", "Spain", "Brazil", group="A"),
        MatchFixture("A4", "group", "France", "Japan", group="A"),
        MatchFixture("A5", "group", "Spain", "Japan", group="A"),
        MatchFixture("A6", "group", "France", "Brazil", group="A"),
    ]
    ratings = {
        "Spain": 1984.02,
        "France": 1948.33,
        "Brazil": 1929.46,
        "Japan": 1650.0,
    }

    outcomes = simulate_group_stage(
        fixtures=fixtures,
        ratings=ratings,
        rng=random.Random(42),
        config=SimulationConfig(max_goals=6),
    )

    outcome = outcomes["A"]
    assert outcome.group == "A"
    assert len(outcome.standings) == 4
    assert outcome.winner in ratings
    assert outcome.runner_up in ratings
    assert outcome.third_place in ratings
    assert all(row.played == 3 for row in outcome.standings)
