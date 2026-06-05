from __future__ import annotations

from src.prediction.core.models import MatchResult


def loser(result: MatchResult) -> str:
    """Return the losing team for a decisive match result."""

    if result.winner == result.team_a:
        return result.team_b
    return result.team_a
