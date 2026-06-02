from __future__ import annotations

import random
from collections import defaultdict

from src.prediction.match import simulate_match
from src.prediction.models import GroupOutcome, MatchFixture, SimulationConfig
from src.prediction.standings import build_group_standings


def simulate_group_stage(
    fixtures: list[MatchFixture],
    ratings: dict[str, float],
    rng: random.Random,
    config: SimulationConfig | None = None,
) -> dict[str, GroupOutcome]:
    config = config or SimulationConfig()
    fixtures_by_group: dict[str, list[MatchFixture]] = defaultdict(list)

    for fixture in fixtures:
        if fixture.group is None:
            raise ValueError(f"Group fixture {fixture.match_id} is missing a group")
        fixtures_by_group[fixture.group].append(fixture)

    outcomes = {}
    for group, group_fixtures in fixtures_by_group.items():
        results = [
            simulate_match(fixture=fixture, ratings=ratings, rng=rng, knockout=False, max_goals=config.max_goals)
            for fixture in group_fixtures
        ]
        standings = build_group_standings(results)

        if len(standings) < 2:
            raise ValueError(f"Group {group} needs at least two teams")

        outcomes[group] = GroupOutcome(
            group=group,
            standings=standings,
            winner=standings[0].team,
            runner_up=standings[1].team,
            third_place=standings[2].team if len(standings) > 2 else None,
        )

    return outcomes
