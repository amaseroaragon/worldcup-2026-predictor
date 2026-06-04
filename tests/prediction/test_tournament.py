import random

from src.prediction.models import MatchResult, TournamentOutcome
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


def mini_knockout_matches() -> list[dict[str, str]]:
    return [
        {"match_id": "M1", "round": "quarter_final", "home": "1A", "away": "2B"},
        {"match_id": "M2", "round": "quarter_final", "home": "1B", "away": "2A"},
        {"match_id": "M3", "round": "quarter_final", "home": "1C", "away": "2D"},
        {"match_id": "M4", "round": "quarter_final", "home": "1D", "away": "2C"},
        {"match_id": "M5", "round": "semi_final", "home": "W1", "away": "W2"},
        {"match_id": "M6", "round": "semi_final", "home": "W3", "away": "W4"},
        {"match_id": "M7", "round": "final", "home": "W5", "away": "W6"},
    ]


def test_simulate_tournament_once_returns_tournament_outcome():
    groups = mini_groups()

    outcome = simulate_tournament_once(
        groups=groups,
        ratings=mini_ratings(groups),
        knockout_matches=mini_knockout_matches(),
        rng=random.Random(42),
    )

    assert isinstance(outcome, TournamentOutcome)


def test_simulate_tournament_once_returns_champion_and_runner_up():
    groups = mini_groups()

    outcome = simulate_tournament_once(
        groups=groups,
        ratings=mini_ratings(groups),
        knockout_matches=mini_knockout_matches(),
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
        knockout_matches=mini_knockout_matches(),
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

    outcome_a = simulate_tournament_once(
        groups,
        ratings,
        knockout_matches=mini_knockout_matches(),
        rng=random.Random(42),
    )
    outcome_b = simulate_tournament_once(
        groups,
        ratings,
        knockout_matches=mini_knockout_matches(),
        rng=random.Random(42),
    )

    assert outcome_a == outcome_b


def test_simulate_tournament_once_uses_updated_elo_in_later_round(monkeypatch):
    groups = mini_groups()
    ratings = mini_ratings(groups)
    observed_ratings = {}

    def fake_simulate_knockout_match(fixture, current_ratings, **kwargs):
        observed_ratings[fixture.match_id] = current_ratings[fixture.team_a]
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

    monkeypatch.setattr(
        "src.prediction.tournament.simulate_knockout_match",
        fake_simulate_knockout_match,
    )

    simulate_tournament_once(
        groups,
        ratings,
        knockout_matches=mini_knockout_matches(),
        rng=random.Random(42),
    )

    assert observed_ratings["M5"] > observed_ratings["M1"]


def test_simulate_tournament_once_fixed_elo_keeps_later_round_rating(monkeypatch):
    groups = mini_groups()
    ratings = mini_ratings(groups)
    observed_ratings = {}
    observed_teams = {}

    def fake_simulate_knockout_match(fixture, current_ratings, **kwargs):
        observed_ratings[fixture.match_id] = current_ratings[fixture.team_a]
        observed_teams[fixture.match_id] = fixture.team_a
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

    monkeypatch.setattr("src.prediction.config.USE_DYNAMIC_ELO_KNOCKOUT", False)
    monkeypatch.setattr("src.prediction.config.USE_DYNAMIC_ELO_GROUP_STAGE", False)
    monkeypatch.setattr(
        "src.prediction.tournament.simulate_knockout_match",
        fake_simulate_knockout_match,
    )

    simulate_tournament_once(
        groups,
        ratings,
        knockout_matches=mini_knockout_matches(),
        rng=random.Random(42),
    )

    assert observed_ratings["M5"] == ratings[observed_teams["M5"]]


def test_simulate_tournament_once_shares_local_elo_from_groups_to_knockout(monkeypatch):
    from src.prediction.group_stage import simulate_group_stage as real_simulate_group_stage

    groups = mini_groups()
    ratings = mini_ratings(groups)
    initial_ratings = ratings.copy()
    group_stage_ratings_id = None
    first_knockout_ratings = None

    def fake_simulate_group_stage(fixtures, local_ratings, **kwargs):
        nonlocal group_stage_ratings_id
        group_stage_ratings_id = id(local_ratings)
        local_ratings["Team 1"] += 25
        return real_simulate_group_stage(fixtures, local_ratings, **kwargs)

    def fake_simulate_knockout_match(fixture, local_ratings, **kwargs):
        nonlocal first_knockout_ratings
        if first_knockout_ratings is None:
            first_knockout_ratings = (id(local_ratings), local_ratings["Team 1"])
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

    monkeypatch.setattr("src.prediction.config.USE_DYNAMIC_ELO_GROUP_STAGE", False)
    monkeypatch.setattr("src.prediction.tournament.simulate_group_stage", fake_simulate_group_stage)
    monkeypatch.setattr(
        "src.prediction.tournament.simulate_knockout_match",
        fake_simulate_knockout_match,
    )

    simulate_tournament_once(groups, ratings, knockout_matches=mini_knockout_matches())

    assert first_knockout_ratings == (group_stage_ratings_id, initial_ratings["Team 1"] + 25)
    assert ratings == initial_ratings
