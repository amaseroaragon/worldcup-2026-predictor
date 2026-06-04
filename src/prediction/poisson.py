from __future__ import annotations

import math


def poisson_probability(k: int, lambda_: float) -> float:
    """
    Returns the probability of scoring exactly k goals under a Poisson model.

    Args:
        k: Number of goals.
        lambda_: Expected goals.

    Returns:
        Probability of scoring exactly k goals.
    """
    if k < 0:
        raise ValueError("k must be non-negative")

    if lambda_ <= 0:
        raise ValueError("lambda_ must be positive")

    return (lambda_**k * math.exp(-lambda_)) / math.factorial(k)


def expected_goals_from_elo(
    elo_a: float,
    elo_b: float,
    base_goals: float = 1.35,
    elo_sensitivity: float = 0.0015,
    min_expected_goals: float = 0.2,
    max_expected_goals: float = 3.5,
    attack_rating_a: float = 1.0,
    defense_rating_a: float = 1.0,
    attack_rating_b: float = 1.0,
    defense_rating_b: float = 1.0,
) -> tuple[float, float]:
    """
    Converts Elo ratings into expected goals for both teams.

    Args:
        elo_a: Elo rating of team A.
        elo_b: Elo rating of team B.
        base_goals: Expected goals for each team when both teams are equally strong.
        elo_sensitivity: How strongly Elo difference affects expected goals.
        min_expected_goals: Lower bound for expected goals.
        max_expected_goals: Upper bound for expected goals.
        attack_rating_a: Team A's goalscoring strength relative to average.
        defense_rating_a: Team A's goals conceded relative to average.
        attack_rating_b: Team B's goalscoring strength relative to average.
        defense_rating_b: Team B's goals conceded relative to average.

    Returns:
        (expected_goals_a, expected_goals_b)
    """
    strength_ratings = (
        attack_rating_a,
        defense_rating_a,
        attack_rating_b,
        defense_rating_b,
    )
    if any(rating <= 0 for rating in strength_ratings):
        raise ValueError("attack and defense ratings must be positive")

    elo_diff = elo_a - elo_b

    expected_goals_a = (
        base_goals
        * math.exp(elo_sensitivity * elo_diff)
        * attack_rating_a
        * defense_rating_b
    )
    expected_goals_b = (
        base_goals
        * math.exp(-elo_sensitivity * elo_diff)
        * attack_rating_b
        * defense_rating_a
    )

    expected_goals_a = min(max(expected_goals_a, min_expected_goals), max_expected_goals)
    expected_goals_b = min(max(expected_goals_b, min_expected_goals), max_expected_goals)

    return expected_goals_a, expected_goals_b


def score_probability(goals_a: int, goals_b: int, expected_goals_a: float, expected_goals_b: float) -> float:
    """
    Returns the probability of a specific scoreline.

    Assumes goals by both teams are independent Poisson variables.
    """
    return poisson_probability(goals_a, expected_goals_a) * poisson_probability(
        goals_b,
        expected_goals_b,
    )


def score_matrix(expected_goals_a: float, expected_goals_b: float, max_goals: int = 10) -> list[list[float]]:
    """
    Returns a matrix of scoreline probabilities.

    matrix[i][j] = probability of team A scoring i goals and team B scoring j goals.
    """
    if max_goals < 0:
        raise ValueError("max_goals must be non-negative")

    matrix = []
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            prob = score_probability(
                goals_a=i,
                goals_b=j,
                expected_goals_a=expected_goals_a,
                expected_goals_b=expected_goals_b,
            )
            row.append(prob)
        matrix.append(row)

    return matrix
