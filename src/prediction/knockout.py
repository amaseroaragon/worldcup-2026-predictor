from __future__ import annotations

import random

from src.prediction.match import simulate_match
from src.prediction.models import GroupOutcome, GroupStandingRow, MatchFixture, MatchResult


def build_knockout_fixtures(knockout_matches: list[dict[str, str]]) -> list[MatchFixture]:
    """Convert configured knockout matches into unresolved fixtures."""

    return [
        MatchFixture(
            match_id=match["match_id"],
            stage=match["round"],
            team_a=None,
            team_b=None,
            source_a=match["home"],
            source_b=match["away"],
        )
        for match in knockout_matches
    ]


def resolve_knockout_fixture(
    fixture: MatchFixture,
    group_outcomes: dict[str, GroupOutcome],
    match_results: dict[str, MatchResult] | None = None,
    third_place_rankings: list[tuple[str, GroupStandingRow]] | None = None,
    used_third_place_groups: set[str] | None = None,
    third_place_placeholder_resolution: dict[str, str] | None = None,
) -> MatchFixture:
    """Resolve one knockout fixture from group outcomes and prior match results."""

    team_a = fixture.team_a or _resolve_knockout_placeholder(
        fixture.source_a,
        group_outcomes,
        match_results or {},
        third_place_rankings or [],
        used_third_place_groups,
        third_place_placeholder_resolution,
    )
    team_b = fixture.team_b or _resolve_knockout_placeholder(
        fixture.source_b,
        group_outcomes,
        match_results or {},
        third_place_rankings or [],
        used_third_place_groups,
        third_place_placeholder_resolution,
    )

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


def rank_third_place_teams(
    group_outcomes: dict[str, GroupOutcome],
) -> list[tuple[str, GroupStandingRow]]:
    """Rank third-place teams by tournament tiebreaker fields."""

    rows = []
    for group, outcome in group_outcomes.items():
        if len(outcome.standings) < 3:
            raise ValueError(f"Group {group} does not have a third-place team")
        rows.append((group, outcome.standings[2]))

    return sorted(
        rows,
        key=lambda row: (
            -row[1].points,
            -row[1].goal_difference,
            -row[1].goals_for,
            row[1].team,
        ),
    )


def build_third_place_placeholder_resolution(
    third_place_rankings: list[tuple[str, GroupStandingRow]],
    third_place_combinations: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Build placeholder mapping for the official best-third combination."""

    best_third_groups = "".join(sorted(group for group, _row in third_place_rankings[:8]))
    if best_third_groups not in third_place_combinations:
        raise ValueError(f"Unknown best third-place combination: {best_third_groups}")
    return third_place_combinations[best_third_groups]


def simulate_knockout_match(
    fixture: MatchFixture,
    ratings: dict[str, float],
    rng: random.Random | None = None,
) -> MatchResult:
    """Simulate a resolved knockout fixture."""

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
    """Simulate a full knockout round and return results plus winners."""

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


def _resolve_knockout_placeholder(
    placeholder: str | None,
    group_outcomes: dict[str, GroupOutcome],
    match_results: dict[str, MatchResult],
    third_place_rankings: list[tuple[str, GroupStandingRow]],
    used_third_place_groups: set[str] | None,
    third_place_placeholder_resolution: dict[str, str] | None,
) -> str:
    if placeholder is None:
        raise ValueError("Missing team and source placeholder")

    if len(placeholder) == 2 and placeholder[0] in {"1", "2"}:
        group = placeholder[1]
        if placeholder[0] == "1":
            return _resolve_group_winner(group, group_outcomes)
        return _resolve_group_runner_up(group, group_outcomes)

    if placeholder.startswith("3") and len(placeholder) > 1:
        return _resolve_third_place_placeholder(
            placeholder,
            group_outcomes,
            third_place_rankings,
            used_third_place_groups,
            third_place_placeholder_resolution,
        )

    if placeholder.startswith("W"):
        result = _get_match_result(placeholder.removeprefix("W"), match_results)
        if result.winner is None:
            raise ValueError(f"Match {placeholder} has no winner")
        return result.winner

    if placeholder.startswith("RU"):
        result = _get_match_result(placeholder.removeprefix("RU"), match_results)
        return _loser(result)

    raise ValueError(f"Invalid knockout placeholder: {placeholder}")


def _resolve_group_winner(
    group: str,
    group_outcomes: dict[str, GroupOutcome],
) -> str:
    outcome = _get_group_outcome(group, group_outcomes)
    if not outcome.winner:
        raise ValueError(f"Group {group} has no winner")
    return outcome.winner


def _resolve_group_runner_up(
    group: str,
    group_outcomes: dict[str, GroupOutcome],
) -> str:
    outcome = _get_group_outcome(group, group_outcomes)
    if not outcome.runner_up:
        raise ValueError(f"Group {group} has no runner-up")
    return outcome.runner_up


def _resolve_third_place_placeholder(
    placeholder: str,
    group_outcomes: dict[str, GroupOutcome],
    third_place_rankings: list[tuple[str, GroupStandingRow]],
    used_third_place_groups: set[str] | None,
    third_place_placeholder_resolution: dict[str, str] | None,
) -> str:
    if used_third_place_groups is None:
        raise ValueError("Third-place placeholder resolution requires used third-place groups")

    if third_place_placeholder_resolution is not None:
        if placeholder not in third_place_placeholder_resolution:
            raise ValueError(f"Unknown third-place placeholder: {placeholder}")

        resolved_placeholder = third_place_placeholder_resolution[placeholder]
        if not resolved_placeholder.startswith("3") or len(resolved_placeholder) != 2:
            raise ValueError(f"Invalid third-place placeholder resolution: {resolved_placeholder}")

        group = resolved_placeholder[1]
        if group in used_third_place_groups:
            raise ValueError(f"Third-place group {group} was already used")
        used_third_place_groups.add(group)
        return _resolve_group_third_place(group, group_outcomes)

    allowed_groups = set(placeholder.removeprefix("3"))
    for group, row in third_place_rankings[:8]:
        if group in allowed_groups and group not in used_third_place_groups:
            used_third_place_groups.add(group)
            return row.team

    raise ValueError(f"Could not resolve third-place placeholder: {placeholder}")


def _resolve_group_third_place(
    group: str,
    group_outcomes: dict[str, GroupOutcome],
) -> str:
    outcome = _get_group_outcome(group, group_outcomes)
    if not outcome.third_place:
        raise ValueError(f"Group {group} has no third-place team")
    return outcome.third_place


def _get_match_result(
    match_ref: str,
    match_results: dict[str, MatchResult],
) -> MatchResult:
    match_id = match_ref if match_ref.startswith("M") else f"M{match_ref}"
    if match_id not in match_results:
        raise ValueError(f"Unknown knockout match placeholder: {match_ref}")
    return match_results[match_id]


def _get_group_outcome(
    group: str,
    group_outcomes: dict[str, GroupOutcome],
) -> GroupOutcome:
    if group not in group_outcomes:
        raise ValueError(f"Unknown group in knockout placeholder: {group}")
    return group_outcomes[group]


def _loser(result: MatchResult) -> str:
    if result.winner == result.team_a:
        return result.team_b
    return result.team_a
