from __future__ import annotations

import random

from src.prediction.models import MatchFixture, MatchResult
from src.prediction.poisson import expected_goals_from_elo, poisson_probability
from src.prediction.recent_form import RecentFormRating
from src.prediction.squad_strength import SquadStrengthRating
from src.prediction.team_strength import TeamStrengthRating
from src.prediction.config import RECENT_FORM_PRIMARY_WINDOW
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
    team_strength_ratings: dict[str, TeamStrengthRating] | None = None,
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
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

    strength_a = team_strength_ratings.get(team_a) if team_strength_ratings else None
    strength_b = team_strength_ratings.get(team_b) if team_strength_ratings else None
    recent_form_a = recent_form_ratings.get(team_a) if recent_form_ratings else None
    recent_form_b = recent_form_ratings.get(team_b) if recent_form_ratings else None
    squad_strength_a = squad_strength_ratings.get(team_a) if squad_strength_ratings else None
    squad_strength_b = squad_strength_ratings.get(team_b) if squad_strength_ratings else None
    expected_goals_a, expected_goals_b = expected_goals_from_elo(
        elo_a,
        elo_b,
        attack_rating_a=strength_a.attack_rating if strength_a else 1.0,
        defense_rating_a=strength_a.defense_rating if strength_a else 1.0,
        attack_rating_b=strength_b.attack_rating if strength_b else 1.0,
        defense_rating_b=strength_b.defense_rating if strength_b else 1.0,
        form_rating_a=(
            recent_form_a.for_window(RECENT_FORM_PRIMARY_WINDOW) if recent_form_a else None
        ),
        form_rating_b=(
            recent_form_b.for_window(RECENT_FORM_PRIMARY_WINDOW) if recent_form_b else None
        ),
        squad_strength_rating_a=(
            squad_strength_a.squad_strength_rating if squad_strength_a else None
        ),
        squad_strength_rating_b=(
            squad_strength_b.squad_strength_rating if squad_strength_b else None
        ),
    )

    if rng is None:
        goals_a = sample_poisson(expected_goals_a, max_goals=max_goals)
        goals_b = sample_poisson(expected_goals_b, max_goals=max_goals)
    else:
        goals_a = sample_poisson(expected_goals_a, max_goals=max_goals, rng=rng)
        goals_b = sample_poisson(expected_goals_b, max_goals=max_goals, rng=rng)

    if goals_a > goals_b:
        return MatchResult(
            team_a,
            team_b,
            goals_a,
            goals_b,
            team_a,
            False,
            "regular_time",
            match_id,
            False,
        )

    if goals_b > goals_a:
        return MatchResult(
            team_a,
            team_b,
            goals_a,
            goals_b,
            team_b,
            False,
            "regular_time",
            match_id,
            False,
        )

    if not knockout:
        return MatchResult(team_a, team_b, goals_a, goals_b, None, True, "draw", match_id, False)

    prob_a_advances = expected_score(elo_a, elo_b)
    winner = team_a if random_source.random() < prob_a_advances else team_b

    return MatchResult(
        team_a,
        team_b,
        goals_a,
        goals_b,
        winner,
        False,
        "tiebreaker",
        match_id,
        False,
    )
