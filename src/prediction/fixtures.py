from __future__ import annotations

from itertools import combinations

from src.prediction.models import MatchFixture


TEAMS_PER_GROUP = 4


def build_group_stage_fixtures(groups: dict[str, list[str]]) -> list[MatchFixture]:
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
