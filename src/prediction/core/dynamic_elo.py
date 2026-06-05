from __future__ import annotations

from src.elo.context import MatchContext
from src.elo.update import match_result, update_rating
from src.prediction.core.models import MatchResult


def update_dynamic_elo_ratings(
    ratings: dict[str, float],
    result: MatchResult,
    *,
    importance: str,
) -> None:
    """Update both teams' local Elo ratings after a simulated World Cup match."""
    team_a_rating = ratings[result.team_a]
    team_b_rating = ratings[result.team_b]
    result_a, result_b = match_result(result.goals_a, result.goals_b)
    goal_diff = result.goals_a - result.goals_b
    context = MatchContext(tournament="FIFA World Cup", importance=importance)

    ratings[result.team_a] = update_rating(
        rating=team_a_rating,
        opponent_rating=team_b_rating,
        actual_score=result_a,
        context=context,
        goal_diff=goal_diff,
    )
    ratings[result.team_b] = update_rating(
        rating=team_b_rating,
        opponent_rating=team_a_rating,
        actual_score=result_b,
        context=context,
        goal_diff=goal_diff,
    )
