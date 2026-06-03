import math

from src.elo.expected import expected_score
from src.elo.context import MatchContext, get_k_factor


MAX_MARGIN_OF_VICTORY_FACTOR = 2.0


def match_result(
    home_score: int,
    away_score: int,
) -> tuple[float, float]:
    """
    Convert match result into Elo scores.

    Returns:
        (home_result, away_result)
    """

    if home_score > away_score:
        return 1.0, 0.0

    if home_score < away_score:
        return 0.0, 1.0

    return 0.5, 0.5


def margin_of_victory_factor(goal_diff: int | float) -> float:
    """
    Return a capped multiplier for the goal difference.
    """

    if goal_diff == 0:
        return 1.0

    return min(
        max(1.0, math.log(abs(goal_diff) + 1)),
        MAX_MARGIN_OF_VICTORY_FACTOR,
    )


def update_rating(
    rating: float,
    opponent_rating: float,
    actual_score: float,
    k_factor: float | None = None,
    context: MatchContext | None = None,
    goal_diff: int | float = 0,
) -> float:
    """
    Update Elo rating for one team.

    actual_score:
    - 1.0 win
    - 0.5 draw
    - 0.0 loss
    """
    expected = expected_score(rating, opponent_rating)
    resolved_k_factor = k_factor if k_factor is not None else get_k_factor(context)
    return (
        rating
        + resolved_k_factor
        * margin_of_victory_factor(goal_diff)
        * (actual_score - expected)
    )
