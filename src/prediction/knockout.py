from __future__ import annotations

import random

from src.prediction.match import simulate_match
from src.prediction.models import MatchFixture, MatchResult


def simulate_knockout_match(
    fixture: MatchFixture,
    ratings: dict[str, float],
    rng: random.Random | None = None,
) -> MatchResult:
    if fixture.stage == "group":
        raise ValueError(f"Knockout fixture {fixture.match_id} cannot have stage='group'")

    if fixture.team_a is None or fixture.team_b is None:
        raise ValueError(f"Knockout fixture {fixture.match_id} must have both teams defined")

    missing_ratings = [team for team in (fixture.team_a, fixture.team_b) if team not in ratings]
    if missing_ratings:
        missing = ", ".join(missing_ratings)
        raise ValueError(f"Missing Elo rating for: {missing}")

    return simulate_match(
        fixture=fixture,
        ratings=ratings,
        rng=rng,
        knockout=True,
    )
