
from src.elo.config import ELO_EXPECTED_SCORE_SCALE


def expected_score(rating_a: float, rating_b: float) -> float:
    """
    Calculate expected score for team A against team B.
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / ELO_EXPECTED_SCORE_SCALE))
