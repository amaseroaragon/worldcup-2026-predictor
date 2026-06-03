import random

from src.prediction.models import TournamentOutcome
from src.prediction.tournament import simulate_tournament_once


def mini_groups() -> dict[str, list[str]]:
    return {
        "A": ["Team 1", "Team 2", "Team 3", "Team 4"],
        "B": ["Team 5", "Team 6", "Team 7", "Team 8"],
        "C": ["Team 9", "Team 10", "Team 11", "Team 12"],
        "D": ["Team 13", "Team 14", "Team 15", "Team 16"],
    }


def mini_ratings(groups: dict[str, list[str]]) -> dict[str, float]:
    return {
        team: 1800.0 - index * 20
        for index, team in enumerate(team for teams in groups.values() for team in teams)
    }


def test_simulate_tournament_once_returns_tournament_outcome():
    groups = mini_groups()

    outcome = simulate_tournament_once(
        groups=groups,
        ratings=mini_ratings(groups),
        rng=random.Random(42),
    )

    assert isinstance(outcome, TournamentOutcome)


def test_simulate_tournament_once_returns_champion_and_runner_up():
    groups = mini_groups()

    outcome = simulate_tournament_once(
        groups=groups,
        ratings=mini_ratings(groups),
        rng=random.Random(42),
    )

    assert outcome.champion is not None
    assert outcome.runner_up is not None
    assert outcome.champion != outcome.runner_up


def test_simulate_tournament_once_returns_match_results():
    groups = mini_groups()

    outcome = simulate_tournament_once(
        groups=groups,
        ratings=mini_ratings(groups),
        rng=random.Random(42),
    )

    assert outcome.match_results
    assert len(outcome.group_outcomes) == 4
    assert len(outcome.quarterfinalists) == 8
    assert len(outcome.semifinalists) == 4
    assert len(outcome.group_stage_eliminated) == 8


def test_simulate_tournament_once_is_reproducible_with_same_seed():
    groups = mini_groups()
    ratings = mini_ratings(groups)

    outcome_a = simulate_tournament_once(groups, ratings, rng=random.Random(42))
    outcome_b = simulate_tournament_once(groups, ratings, rng=random.Random(42))

    assert outcome_a == outcome_b
