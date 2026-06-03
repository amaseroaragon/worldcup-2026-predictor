from __future__ import annotations

import random

from src.prediction.fixtures import build_group_stage_fixtures
from src.prediction.group_stage import simulate_group_stage
from src.prediction.knockout import resolve_knockout_fixture, simulate_knockout_round
from src.prediction.models import GroupOutcome, MatchFixture, MatchResult, TournamentOutcome


REQUIRED_MINI_TOURNAMENT_GROUPS = ("A", "B", "C", "D")


def simulate_tournament_once(
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    rng: random.Random | None = None,
) -> TournamentOutcome:
    _validate_mini_tournament_groups(groups)
    rng = rng or random.Random()

    group_fixtures = build_group_stage_fixtures(groups)
    group_outcomes = simulate_group_stage(group_fixtures, ratings, rng=rng)

    quarterfinal_fixtures = [
        resolve_knockout_fixture(fixture, group_outcomes)
        for fixture in _build_quarterfinal_fixtures()
    ]
    quarterfinal_results, quarterfinal_winners = simulate_knockout_round(
        quarterfinal_fixtures,
        ratings,
        rng=rng,
    )

    semifinal_fixtures = _build_semifinal_fixtures(quarterfinal_winners)
    semifinal_results, semifinal_winners = simulate_knockout_round(
        semifinal_fixtures,
        ratings,
        rng=rng,
    )

    final_fixture = MatchFixture(
        match_id="final",
        stage="final",
        team_a=semifinal_winners[0],
        team_b=semifinal_winners[1],
    )
    final_results, final_winners = simulate_knockout_round([final_fixture], ratings, rng=rng)
    champion = final_winners[0]
    runner_up = _loser(final_results[0])

    quarterfinalists = {team for fixture in quarterfinal_fixtures for team in (fixture.team_a, fixture.team_b)}
    all_teams = {team for teams in groups.values() for team in teams}

    return TournamentOutcome(
        champion=champion,
        runner_up=runner_up,
        semifinalists=set(quarterfinal_winners),
        quarterfinalists=quarterfinalists,
        group_stage_eliminated=all_teams - quarterfinalists,
        group_outcomes=group_outcomes,
        match_results=[
            *_group_match_results(group_outcomes),
            *quarterfinal_results,
            *semifinal_results,
            *final_results,
        ],
    )


def _validate_mini_tournament_groups(groups: dict[str, list[str]]) -> None:
    missing = set(REQUIRED_MINI_TOURNAMENT_GROUPS) - set(groups)
    extra = set(groups) - set(REQUIRED_MINI_TOURNAMENT_GROUPS)
    if missing or extra:
        raise ValueError("Mini tournament V1 requires exactly groups A, B, C and D")


def _build_quarterfinal_fixtures() -> list[MatchFixture]:
    return [
        MatchFixture("quarterfinal_1", "quarterfinal", None, None, source_a="winner_group_A", source_b="runner_up_group_B"),
        MatchFixture("quarterfinal_2", "quarterfinal", None, None, source_a="winner_group_B", source_b="runner_up_group_A"),
        MatchFixture("quarterfinal_3", "quarterfinal", None, None, source_a="winner_group_C", source_b="runner_up_group_D"),
        MatchFixture("quarterfinal_4", "quarterfinal", None, None, source_a="winner_group_D", source_b="runner_up_group_C"),
    ]


def _build_semifinal_fixtures(quarterfinal_winners: list[str]) -> list[MatchFixture]:
    return [
        MatchFixture("semifinal_1", "semifinal", quarterfinal_winners[0], quarterfinal_winners[1]),
        MatchFixture("semifinal_2", "semifinal", quarterfinal_winners[2], quarterfinal_winners[3]),
    ]


def _group_match_results(group_outcomes: dict[str, GroupOutcome]) -> list[MatchResult]:
    return [
        result
        for group in REQUIRED_MINI_TOURNAMENT_GROUPS
        for result in group_outcomes[group].match_results
    ]


def _loser(result: MatchResult) -> str:
    if result.winner == result.team_a:
        return result.team_b
    return result.team_a
