from __future__ import annotations

from dataclasses import dataclass
import random

from src.prediction.poisson import expected_goals_from_elo, poisson_probability
from src.elo.expected import expected_score


@dataclass(frozen=True)
class MatchResult:
    team_a: str
    team_b: str
    goals_a: int
    goals_b: int
    winner: str | None
    is_draw: bool
    decided_by: str


def sample_poisson(lambda_: float, max_goals: int = 10) -> int:
    """
    Samples a goal count from a truncated Poisson distribution.

    max_goals caps rare extreme scorelines.
    """
    probabilities = [poisson_probability(k, lambda_) for k in range(max_goals + 1)]
    total = sum(probabilities)
    normalized = [p / total for p in probabilities]

    return random.choices(
        population=list(range(max_goals + 1)),
        weights=normalized,
        k=1,
    )[0]


def simulate_match(team_a: str, team_b: str, elo_a: float, elo_b: float, knockout: bool = False, max_goals: int = 10) -> MatchResult:
    """
    Simulates a single football match.

    In group-stage mode, draws are allowed.
    In knockout mode, draws are resolved by an Elo-weighted tiebreaker.
    """
    expected_goals_a, expected_goals_b = expected_goals_from_elo(elo_a, elo_b)

    goals_a = sample_poisson(expected_goals_a, max_goals=max_goals)
    goals_b = sample_poisson(expected_goals_b, max_goals=max_goals)

    if goals_a > goals_b:
        return MatchResult(team_a, team_b, goals_a, goals_b, team_a, False, "regular_time")

    if goals_b > goals_a:
        return MatchResult(team_a, team_b, goals_a, goals_b, team_b, False, "regular_time")

    if not knockout:
        return MatchResult(team_a, team_b, goals_a, goals_b, None, True, "draw")

    prob_a_advances = expected_score(elo_a, elo_b)
    winner = team_a if random.random() < prob_a_advances else team_b

    return MatchResult(team_a, team_b, goals_a, goals_b, winner, False, "tiebreaker")
