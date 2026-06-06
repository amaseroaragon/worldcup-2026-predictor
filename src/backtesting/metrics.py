from __future__ import annotations

from collections.abc import Mapping, Sequence


ProbabilityRow = Mapping[str, object]


def champion_rank(probability_rows: Sequence[ProbabilityRow], real_champion: str) -> int | None:
    """Return the 1-based champion-probability rank for the real champion."""

    sorted_rows = _sorted_by_probability(probability_rows, "champion_probability")
    for index, row in enumerate(sorted_rows, start=1):
        if row["team"] == real_champion:
            return index
    return None


def real_champion_probability(
    probability_rows: Sequence[ProbabilityRow],
    real_champion: str,
) -> float:
    """Return the champion probability assigned to the actual champion."""

    return probability_for_team(probability_rows, real_champion, "champion_probability")


def top_k_hit(probability_rows: Sequence[ProbabilityRow], real_champion: str, k: int) -> bool:
    """Return whether the real champion appears in the top-k champion ranking."""

    if k <= 0:
        raise ValueError("k must be positive")

    top_teams = [
        str(row["team"])
        for row in _sorted_by_probability(probability_rows, "champion_probability")[:k]
    ]
    return real_champion in top_teams


def brier_champion(probability_rows: Sequence[ProbabilityRow], real_champion: str) -> float:
    """Return the mean binary Brier score for the champion event across teams."""

    return brier_binary_event(
        probability_rows,
        actual_positive_teams={real_champion},
        probability_column="champion_probability",
    )


def brier_binary_event(
    probability_rows: Sequence[ProbabilityRow],
    *,
    actual_positive_teams: set[str],
    probability_column: str,
) -> float:
    """Return mean binary Brier score for one event across all teams."""

    if not probability_rows:
        raise ValueError("probability_rows must not be empty")

    squared_errors = []
    for row in probability_rows:
        team = str(row["team"])
        probability = float(row.get(probability_column, 0.0) or 0.0)
        actual = 1.0 if team in actual_positive_teams else 0.0
        squared_errors.append((probability - actual) ** 2)

    return sum(squared_errors) / len(squared_errors)


def probability_for_team(
    probability_rows: Sequence[ProbabilityRow],
    team: str,
    probability_column: str,
) -> float:
    """Return one probability value for a team, or 0.0 when the team is missing."""

    for row in probability_rows:
        if row["team"] == team:
            return float(row.get(probability_column, 0.0) or 0.0)
    return 0.0


def _sorted_by_probability(
    probability_rows: Sequence[ProbabilityRow],
    probability_column: str,
) -> list[ProbabilityRow]:
    return sorted(
        probability_rows,
        key=lambda row: float(row.get(probability_column, 0.0) or 0.0),
        reverse=True,
    )

