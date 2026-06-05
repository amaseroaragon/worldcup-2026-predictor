from __future__ import annotations

from itertools import combinations

from src.prediction.core.models import MatchFixture


TEAMS_PER_GROUP = 4


def build_group_stage_fixtures(
    groups: dict[str, list[str]],
    group_matches: list[dict[str, str | int]] | None = None,
) -> list[MatchFixture]:
    """Create group-stage fixtures from configuration or legacy round-robin generation."""
    if group_matches is not None:
        return _build_configured_group_stage_fixtures(groups, group_matches)

    fixtures = []

    for group, teams in groups.items():
        if len(teams) != TEAMS_PER_GROUP:
            raise ValueError(f"Group {group} must have exactly {TEAMS_PER_GROUP} teams")

        for index, (team_a, team_b) in enumerate(combinations(teams, 2), start=1):
            fixtures.append(
                MatchFixture(
                    match_id=f"group_{group}_{index}",
                    stage="group",
                    group=group,
                    team_a=team_a,
                    team_b=team_b,
                )
            )

    return fixtures


def _build_configured_group_stage_fixtures(
    groups: dict[str, list[str]],
    group_matches: list[dict[str, str | int]],
) -> list[MatchFixture]:
    fixtures = []
    for match in group_matches:
        group = str(match["group"])
        team_a = str(match["home"])
        team_b = str(match["away"])
        if group not in groups:
            raise ValueError(f"Unknown group in group match: {group}")
        if team_a not in groups[group] or team_b not in groups[group]:
            raise ValueError(f"Group match {match['match_id']} contains a team outside group {group}")

        fixtures.append(
            MatchFixture(
                match_id=str(match["match_id"]),
                stage="group",
                group=group,
                team_a=team_a,
                team_b=team_b,
                matchday=int(match["matchday"]),
            )
        )

    return sorted(fixtures, key=lambda fixture: (fixture.matchday or 0, fixture.match_id))
