

def expected_score(rating_a: float, rating_b: float) -> float:
    """
    Calculate expected score for team A against team B.
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))