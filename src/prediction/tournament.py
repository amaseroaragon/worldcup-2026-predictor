from __future__ import annotations

import random

from src.prediction.fixtures import build_group_stage_fixtures
from src.prediction.group_stage import simulate_group_stage
from src.prediction.knockout import (
    build_knockout_fixtures,
    build_third_place_placeholder_resolution,
    rank_third_place_teams,
    resolve_knockout_fixture,
    simulate_knockout_match,
    update_knockout_elo_ratings,
)
from src.prediction import config
from src.prediction.models import GroupOutcome, MatchFixture, MatchResult, TournamentOutcome
from src.prediction.recent_form import RecentFormRating
from src.prediction.squad_strength import SquadStrengthRating
from src.prediction.team_strength import TeamStrengthRating


ROUND_OF_32 = "round_of_32"
ROUND_OF_16 = "round_of_16"
QUARTER_FINAL = "quarter_final"
SEMI_FINAL = "semi_final"
FINAL = "final"


def simulate_tournament_once(
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    rng: random.Random | None = None,
    knockout_matches: list[dict[str, str]] | None = None,
    third_place_combinations: dict[str, dict[str, str]] | None = None,
    team_strength_ratings: dict[str, TeamStrengthRating] | None = None,
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    group_matches: list[dict[str, str | int]] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
) -> TournamentOutcome:
    """Simulate one full tournament from group stage through final."""

    if knockout_matches is None:
        raise ValueError("knockout_matches must be provided")

    rng = rng or random.Random()
    simulation_ratings = ratings.copy()

    group_fixtures = build_group_stage_fixtures(groups, group_matches)
    group_outcomes = simulate_group_stage(
        group_fixtures,
        simulation_ratings,
        rng=rng,
        team_strength_ratings=team_strength_ratings,
        recent_form_ratings=recent_form_ratings,
        squad_strength_ratings=squad_strength_ratings,
    )
    knockout_fixtures = build_knockout_fixtures(knockout_matches)

    match_results_by_id: dict[str, MatchResult] = {}
    knockout_results: list[MatchResult] = []
    used_third_place_groups: set[str] = set()
    third_place_rankings = rank_third_place_teams(group_outcomes)
    third_place_placeholder_resolution = (
        build_third_place_placeholder_resolution(third_place_rankings, third_place_combinations)
        if third_place_combinations is not None
        else None
    )
    final_result: MatchResult | None = None
    first_knockout_round: str | None = None
    first_knockout_teams: set[str] = set()
    teams_by_round: dict[str, set[str]] = {
        ROUND_OF_32: set(),
        ROUND_OF_16: set(),
        QUARTER_FINAL: set(),
        SEMI_FINAL: set(),
    }

    for fixture in knockout_fixtures:
        resolved_fixture = resolve_knockout_fixture(
            fixture=fixture,
            group_outcomes=group_outcomes,
            match_results=match_results_by_id,
            third_place_rankings=third_place_rankings,
            used_third_place_groups=used_third_place_groups,
            third_place_placeholder_resolution=third_place_placeholder_resolution,
        )
        if first_knockout_round is None:
            first_knockout_round = resolved_fixture.stage
        if resolved_fixture.stage == first_knockout_round:
            first_knockout_teams.update({resolved_fixture.team_a, resolved_fixture.team_b})
        if resolved_fixture.stage in teams_by_round:
            teams_by_round[resolved_fixture.stage].update(
                {resolved_fixture.team_a, resolved_fixture.team_b}
            )

        result = simulate_knockout_match(
            resolved_fixture,
            simulation_ratings,
            rng=rng,
            team_strength_ratings=team_strength_ratings,
            recent_form_ratings=recent_form_ratings,
            squad_strength_ratings=squad_strength_ratings,
        )
        knockout_results.append(result)
        match_results_by_id[result.match_id] = result
        if config.USE_DYNAMIC_ELO_KNOCKOUT:
            update_knockout_elo_ratings(simulation_ratings, resolved_fixture, result)
        if resolved_fixture.stage == FINAL:
            final_result = result

    if final_result is None:
        raise ValueError("Knockout bracket must contain a final match")

    champion = final_result.winner
    runner_up = _loser(final_result)
    all_teams = {team for teams in groups.values() for team in teams}

    return TournamentOutcome(
        champion=champion,
        runner_up=runner_up,
        semifinalists=teams_by_round[SEMI_FINAL],
        quarterfinalists=teams_by_round[QUARTER_FINAL],
        round_of_16=teams_by_round[ROUND_OF_16],
        round_of_32=teams_by_round[ROUND_OF_32],
        group_stage_eliminated=all_teams - first_knockout_teams,
        group_outcomes=group_outcomes,
        match_results=[
            *_group_match_results(group_outcomes),
            *knockout_results,
        ],
    )


def _group_match_results(group_outcomes: dict[str, GroupOutcome]) -> list[MatchResult]:
    return [
        result
        for group in group_outcomes
        for result in group_outcomes[group].match_results
    ]


def _loser(result: MatchResult) -> str:
    if result.winner == result.team_a:
        return result.team_b
    return result.team_a
