from __future__ import annotations

from src.prediction.core.models import GroupStandingRow, MatchResult


def build_group_standings(results: list[MatchResult]) -> list[GroupStandingRow]:
    """Build sorted group standings from match results."""

    rows: dict[str, GroupStandingRow] = {}

    for result in results:
        team_a_row = rows.setdefault(result.team_a, GroupStandingRow(team=result.team_a))
        team_b_row = rows.setdefault(result.team_b, GroupStandingRow(team=result.team_b))

        team_a_row.played += 1
        team_b_row.played += 1
        team_a_row.goals_for += result.goals_a
        team_a_row.goals_against += result.goals_b
        team_b_row.goals_for += result.goals_b
        team_b_row.goals_against += result.goals_a

        if result.goals_a > result.goals_b:
            team_a_row.points += 3
            team_a_row.wins += 1
            team_b_row.losses += 1
        elif result.goals_b > result.goals_a:
            team_b_row.points += 3
            team_b_row.wins += 1
            team_a_row.losses += 1
        else:
            team_a_row.points += 1
            team_b_row.points += 1
            team_a_row.draws += 1
            team_b_row.draws += 1

    return sort_group_standings(list(rows.values()))


def sort_group_standings(rows: list[GroupStandingRow]) -> list[GroupStandingRow]:
    """Sort standings by points, goal difference, goals for, then team name."""

    return sorted(
        rows,
        key=lambda row: (
            -row.points,
            -row.goal_difference,
            -row.goals_for,
            row.team,
        ),
    )
