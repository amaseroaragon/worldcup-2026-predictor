from __future__ import annotations

import random
from collections import defaultdict

from src.prediction import config as prediction_config
from src.prediction.dynamic_elo import update_dynamic_elo_ratings
from src.prediction.match import simulate_match
from src.prediction.models import GroupOutcome, MatchFixture, MatchResult, SimulationConfig
from src.prediction.recent_form import RecentFormRating
from src.prediction.squad_strength import SquadStrengthRating
from src.prediction.standings import build_group_standings
from src.prediction.team_strength import TeamStrengthRating


TEAMS_PER_GROUP = 4
MATCHES_PER_GROUP = 6


def simulate_group_stage(
    fixtures: list[MatchFixture],
    ratings: dict[str, float],
    rng: random.Random | None = None,
    config: SimulationConfig | None = None,
    team_strength_ratings: dict[str, TeamStrengthRating] | None = None,
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
) -> dict[str, GroupOutcome]:
    """Simulate all group-stage fixtures and return outcomes by group."""

    config = config or SimulationConfig()
    rng = rng or random.Random(config.random_seed)
    fixtures_by_group: dict[str, list[MatchFixture]] = defaultdict(list)

    for fixture in fixtures:
        if fixture.stage != "group":
            raise ValueError(f"Fixture {fixture.match_id} must have stage='group'")
        if fixture.group is None:
            raise ValueError(f"Group fixture {fixture.match_id} is missing a group")
        missing_ratings = [team for team in (fixture.team_a, fixture.team_b) if team not in ratings]
        if missing_ratings:
            missing = ", ".join(missing_ratings)
            raise ValueError(f"Missing Elo rating for: {missing}")
        fixtures_by_group[fixture.group].append(fixture)

    for group, group_fixtures in fixtures_by_group.items():
        teams = {team for fixture in group_fixtures for team in (fixture.team_a, fixture.team_b)}
        if len(teams) != TEAMS_PER_GROUP or len(group_fixtures) != MATCHES_PER_GROUP:
            raise ValueError(
                f"Group {group} must have {TEAMS_PER_GROUP} teams and {MATCHES_PER_GROUP} fixtures"
            )

    results_by_group: dict[str, list[MatchResult]] = defaultdict(list)
    for fixture in fixtures:
        result = simulate_match(
            fixture=fixture,
            ratings=ratings,
            rng=rng,
            knockout=False,
            max_goals=config.max_goals,
            team_strength_ratings=team_strength_ratings,
            recent_form_ratings=recent_form_ratings,
            squad_strength_ratings=squad_strength_ratings,
        )
        results_by_group[fixture.group].append(result)
        if prediction_config.USE_DYNAMIC_ELO_GROUP_STAGE:
            update_dynamic_elo_ratings(ratings, result, importance="group")

    outcomes = {}
    for group, group_fixtures in fixtures_by_group.items():
        results = results_by_group[group]
        standings = build_group_standings(results)

        outcomes[group] = GroupOutcome(
            group=group,
            standings=standings,
            winner=standings[0].team,
            runner_up=standings[1].team,
            third_place=standings[2].team if len(standings) > 2 else None,
            match_results=results,
        )

    return outcomes
