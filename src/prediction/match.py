from __future__ import annotations

import random

from src.prediction.models import MatchFixture, MatchResult
from src.prediction.poisson import expected_goals_from_elo, poisson_probability
from src.elo.expected import expected_score



def sample_poisson(lambda_: float, max_goals: int = 10, rng: random.Random | None = None) -> int:
    """
    Samples a goal count from a truncated Poisson distribution.

    max_goals caps rare extreme scorelines.
    """
    probabilities = [poisson_probability(k, lambda_) for k in range(max_goals + 1)]
    total = sum(probabilities)
    normalized = [p / total for p in probabilities]

    random_source = rng or random
    return random_source.choices(
        population=list(range(max_goals + 1)),
        weights=normalized,
        k=1,
    )[0]


def simulate_match(
    team_a: str | MatchFixture | None = None,
    team_b: str | None = None,
    elo_a: float | None = None,
    elo_b: float | None = None,
    knockout: bool = False,
    max_goals: int = 10,
    rng: random.Random | None = None,
    ratings: dict[str, float] | None = None,
    fixture: MatchFixture | None = None,
) -> MatchResult:
    """
    Simulates a single football match.

    In group-stage mode, draws are allowed.
    In knockout mode, draws are resolved by an Elo-weighted tiebreaker.
    """
    if fixture is None and isinstance(team_a, MatchFixture):
        fixture = team_a

    match_id: str | None = None
    if fixture is not None:
        if ratings is None:
            raise ValueError("ratings are required when simulating a MatchFixture")
        team_a = fixture.team_a
        team_b = fixture.team_b
        elo_a = ratings[team_a]
        elo_b = ratings[team_b]
        match_id = fixture.match_id

    if team_a is None or team_b is None or elo_a is None or elo_b is None:
        raise ValueError("team_a, team_b, elo_a and elo_b are required")

    random_source = rng or random

    expected_goals_a, expected_goals_b = expected_goals_from_elo(elo_a, elo_b)

    if rng is None:
        goals_a = sample_poisson(expected_goals_a, max_goals=max_goals)
        goals_b = sample_poisson(expected_goals_b, max_goals=max_goals)
    else:
        goals_a = sample_poisson(expected_goals_a, max_goals=max_goals, rng=rng)
        goals_b = sample_poisson(expected_goals_b, max_goals=max_goals, rng=rng)

    if goals_a > goals_b:
        return MatchResult(team_a, team_b, goals_a, goals_b, team_a, False, "regular_time", match_id, False)

    if goals_b > goals_a:
        return MatchResult(team_a, team_b, goals_a, goals_b, team_b, False, "regular_time", match_id, False)

    if not knockout:
        return MatchResult(team_a, team_b, goals_a, goals_b, None, True, "draw", match_id, False)

    prob_a_advances = expected_score(elo_a, elo_b)
    winner = team_a if random_source.random() < prob_a_advances else team_b

    return MatchResult(team_a, team_b, goals_a, goals_b, winner, False, "tiebreaker", match_id, False)
