from __future__ import annotations

import random
from dataclasses import dataclass

from src.prediction.core.models import MatchFixture, MatchResult
from src.prediction.core.poisson import expected_goals_from_elo, poisson_probability
from src.prediction.metrics.recent_form import RecentFormRating
from src.prediction.metrics.squad_strength import SquadStrengthRating
from src.prediction.metrics.team_strength import TeamStrengthRating
from src.prediction.config import (
    RECENT_FORM_PRIMARY_WINDOW,
    TIEBREAKER_EXPECTED_GOALS_WEIGHT,
    USE_MODEL_BASED_KNOCKOUT_TIEBREAKER,
)
from src.prediction.settings import DEFAULT_MAX_GOALS
from src.elo.expected import expected_score


@dataclass(frozen=True)
class MatchSimulationInput:
    team_a: str
    team_b: str
    elo_a: float
    elo_b: float
    match_id: str | None


def sample_poisson(
    lambda_: float,
    max_goals: int = DEFAULT_MAX_GOALS,
    rng: random.Random | None = None,
) -> int:
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
    max_goals: int = DEFAULT_MAX_GOALS,
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
    In knockout mode, draws are resolved by a model-weighted tiebreaker.
    """
    match_input = _resolve_match_input(
        team_a=team_a,
        team_b=team_b,
        elo_a=elo_a,
        elo_b=elo_b,
        ratings=ratings,
        fixture=fixture,
    )
    random_source = rng or random
    expected_goals_a, expected_goals_b = expected_goals_from_elo(
        match_input.elo_a,
        match_input.elo_b,
        **_expected_goals_feature_kwargs(
            team_a=match_input.team_a,
            team_b=match_input.team_b,
            team_strength_ratings=team_strength_ratings,
            recent_form_ratings=recent_form_ratings,
            squad_strength_ratings=squad_strength_ratings,
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
            match_input.team_a,
            match_input.team_b,
            goals_a,
            goals_b,
            match_input.team_a,
            False,
            "regular_time",
            match_input.match_id,
            False,
        )

    if goals_b > goals_a:
        return MatchResult(
            match_input.team_a,
            match_input.team_b,
            goals_a,
            goals_b,
            match_input.team_b,
            False,
            "regular_time",
            match_input.match_id,
            False,
        )

    if not knockout:
        return MatchResult(
            match_input.team_a,
            match_input.team_b,
            goals_a,
            goals_b,
            None,
            True,
            "draw",
            match_input.match_id,
            False,
        )

    prob_a_advances = knockout_tiebreaker_probability(
        match_input.elo_a,
        match_input.elo_b,
        expected_goals_a,
        expected_goals_b,
    )
    winner = match_input.team_a if random_source.random() < prob_a_advances else match_input.team_b

    return MatchResult(
        match_input.team_a,
        match_input.team_b,
        goals_a,
        goals_b,
        winner,
        False,
        "tiebreaker",
        match_input.match_id,
        False,
    )


def _resolve_match_input(
    team_a: str | MatchFixture | None,
    team_b: str | None,
    elo_a: float | None,
    elo_b: float | None,
    ratings: dict[str, float] | None,
    fixture: MatchFixture | None,
) -> MatchSimulationInput:
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

    return MatchSimulationInput(
        team_a=team_a,
        team_b=team_b,
        elo_a=elo_a,
        elo_b=elo_b,
        match_id=match_id,
    )


def _expected_goals_feature_kwargs(
    team_a: str,
    team_b: str,
    team_strength_ratings: dict[str, TeamStrengthRating] | None,
    recent_form_ratings: dict[str, RecentFormRating] | None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None,
) -> dict[str, float | None]:
    strength_a = team_strength_ratings.get(team_a) if team_strength_ratings else None
    strength_b = team_strength_ratings.get(team_b) if team_strength_ratings else None
    recent_form_a = recent_form_ratings.get(team_a) if recent_form_ratings else None
    recent_form_b = recent_form_ratings.get(team_b) if recent_form_ratings else None
    squad_strength_a = squad_strength_ratings.get(team_a) if squad_strength_ratings else None
    squad_strength_b = squad_strength_ratings.get(team_b) if squad_strength_ratings else None

    return {
        "attack_rating_a": strength_a.attack_rating if strength_a else 1.0,
        "defense_rating_a": strength_a.defense_rating if strength_a else 1.0,
        "attack_rating_b": strength_b.attack_rating if strength_b else 1.0,
        "defense_rating_b": strength_b.defense_rating if strength_b else 1.0,
        "form_rating_a": (
            recent_form_a.for_window(RECENT_FORM_PRIMARY_WINDOW) if recent_form_a else None
        ),
        "form_rating_b": (
            recent_form_b.for_window(RECENT_FORM_PRIMARY_WINDOW) if recent_form_b else None
        ),
        "squad_strength_rating_a": (
            squad_strength_a.squad_strength_rating if squad_strength_a else None
        ),
        "squad_strength_rating_b": (
            squad_strength_b.squad_strength_rating if squad_strength_b else None
        ),
    }


def knockout_tiebreaker_probability(
    elo_a: float,
    elo_b: float,
    expected_goals_a: float,
    expected_goals_b: float,
) -> float:
    """Calculate team A's probability of advancing after a knockout draw."""
    elo_probability = expected_score(elo_a, elo_b)
    if not USE_MODEL_BASED_KNOCKOUT_TIEBREAKER:
        return elo_probability

    total_expected_goals = expected_goals_a + expected_goals_b
    if total_expected_goals <= 0:
        return elo_probability

    expected_goals_probability = expected_goals_a / total_expected_goals
    weight = min(max(TIEBREAKER_EXPECTED_GOALS_WEIGHT, 0.0), 1.0)
    return (1 - weight) * elo_probability + weight * expected_goals_probability
