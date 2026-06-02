from src.elo.expected import expected_score

def match_result(home_score: int, away_score: int) -> tuple[float, float]:
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


def update_rating(rating: float, opponent_rating: float, actual_score: float, k_factor: float) -> float:
    """
    Update Elo rating for one team.

    actual_score:
    - 1.0 win
    - 0.5 draw
    - 0.0 loss
    """
    expected = expected_score(rating, opponent_rating)
    return rating + k_factor * (actual_score - expected)