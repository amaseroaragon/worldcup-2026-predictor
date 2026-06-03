from __future__ import annotations

import random

from src.prediction.match import simulate_match
from src.prediction.models import GroupOutcome, MatchFixture, MatchResult


def resolve_knockout_fixture(
    fixture: MatchFixture,
    group_outcomes: dict[str, GroupOutcome],
) -> MatchFixture:
    team_a = fixture.team_a or _resolve_group_placeholder(fixture.source_a, group_outcomes)
    team_b = fixture.team_b or _resolve_group_placeholder(fixture.source_b, group_outcomes)

    return MatchFixture(
        match_id=fixture.match_id,
        stage=fixture.stage,
        team_a=team_a,
        team_b=team_b,
        group=fixture.group,
        source_a=fixture.source_a,
        source_b=fixture.source_b,
        date=fixture.date,
    )


def _resolve_group_placeholder(
    placeholder: str | None,
    group_outcomes: dict[str, GroupOutcome],
) -> str:
    if placeholder is None:
        raise ValueError("Missing team and source placeholder")

    if placeholder.startswith("winner_group_"):
        group = placeholder.removeprefix("winner_group_")
        outcome = _get_group_outcome(group, group_outcomes)
        if not outcome.winner:
            raise ValueError(f"Group {group} has no winner")
        return outcome.winner

    if placeholder.startswith("runner_up_group_"):
        group = placeholder.removeprefix("runner_up_group_")
        outcome = _get_group_outcome(group, group_outcomes)
        if not outcome.runner_up:
            raise ValueError(f"Group {group} has no runner-up")
        return outcome.runner_up

    raise ValueError(f"Invalid knockout placeholder: {placeholder}")


def _get_group_outcome(
    group: str,
    group_outcomes: dict[str, GroupOutcome],
) -> GroupOutcome:
    if group not in group_outcomes:
        raise ValueError(f"Unknown group in knockout placeholder: {group}")
    return group_outcomes[group]


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


def simulate_knockout_round(
    fixtures: list[MatchFixture],
    ratings: dict[str, float],
    rng: random.Random | None = None,
) -> tuple[list[MatchResult], list[str]]:
    if not fixtures:
        raise ValueError("Knockout round must contain at least one fixture")

    results = [
        simulate_knockout_match(
            fixture=fixture,
            ratings=ratings,
            rng=rng,
        )
        for fixture in fixtures
    ]

    winners = [result.winner for result in results]

    return results, winners
