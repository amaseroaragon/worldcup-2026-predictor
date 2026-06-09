from __future__ import annotations

from collections import defaultdict
from statistics import mean

from src.prediction.core.models import TournamentOutcome


ADVANCEMENT_FIELDS = (
    "round_of_32",
    "round_of_16",
    "quarterfinalists",
    "semifinalists",
)


def select_representative_outcome(
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
) -> TournamentOutcome:
    """Select the complete simulation closest to aggregate tournament behavior.

    Distance combines normalized final-finish tier, group position, and binary
    advancement events. Each component is averaged across teams so large rounds
    do not dominate merely because they contain more participants.
    """
    if not outcomes:
        raise ValueError("outcomes must not be empty")

    teams = [team for group_teams in groups.values() for team in group_teams]
    aggregate = _aggregate_targets(outcomes, teams)
    return min(
        outcomes,
        key=lambda outcome: _outcome_distance(outcome, teams, aggregate),
    )


def representative_outcome_distance(
    outcome: TournamentOutcome,
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
) -> float:
    """Expose the representative-distance metric for diagnostics and tests."""
    teams = [team for group_teams in groups.values() for team in group_teams]
    return _outcome_distance(outcome, teams, _aggregate_targets(outcomes, teams))


def _aggregate_targets(
    outcomes: list[TournamentOutcome],
    teams: list[str],
) -> dict[str, dict[str, float]]:
    values: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for outcome in outcomes:
        group_positions = _group_positions(outcome)
        for team in teams:
            values[team]["finish"].append(float(_finish_tier(outcome, team, group_positions)))
            values[team]["group_position"].append(float(group_positions[team]))
            for field in ADVANCEMENT_FIELDS:
                values[team][field].append(float(team in getattr(outcome, field)))
            values[team]["finalist"].append(float(team in {outcome.champion, outcome.runner_up}))
            values[team]["champion"].append(float(team == outcome.champion))

    return {
        team: {metric: mean(samples) for metric, samples in metrics.items()}
        for team, metrics in values.items()
    }


def _outcome_distance(
    outcome: TournamentOutcome,
    teams: list[str],
    aggregate: dict[str, dict[str, float]],
) -> float:
    group_positions = _group_positions(outcome)
    finish_distance = mean(
        ((_finish_tier(outcome, team, group_positions) - aggregate[team]["finish"]) / 48) ** 2
        for team in teams
    )
    group_position_distance = mean(
        ((group_positions[team] - aggregate[team]["group_position"]) / 4) ** 2
        for team in teams
    )
    advancement_metrics = (*ADVANCEMENT_FIELDS, "finalist", "champion")
    advancement_distance = mean(
        (
            _event_value(outcome, team, metric)
            - aggregate[team][metric]
        )
        ** 2
        for team in teams
        for metric in advancement_metrics
    )
    return finish_distance + group_position_distance + advancement_distance


def _group_positions(outcome: TournamentOutcome) -> dict[str, int]:
    return {
        row.team: position
        for group_outcome in outcome.group_outcomes.values()
        for position, row in enumerate(group_outcome.standings, start=1)
    }


def _event_value(outcome: TournamentOutcome, team: str, metric: str) -> float:
    if metric == "finalist":
        return float(team in {outcome.champion, outcome.runner_up})
    if metric == "champion":
        return float(team == outcome.champion)
    return float(team in getattr(outcome, metric))


def _finish_tier(
    outcome: TournamentOutcome,
    team: str,
    group_positions: dict[str, int],
) -> int:
    if team == outcome.champion:
        return 1
    if team == outcome.runner_up:
        return 2
    if team in outcome.semifinalists:
        return 3
    if team in outcome.quarterfinalists:
        return 5
    if team in outcome.round_of_16:
        return 9
    if team in outcome.round_of_32:
        return 17
    return 32 + group_positions[team]
