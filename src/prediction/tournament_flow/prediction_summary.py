from __future__ import annotations

import random

from src.prediction.core.models import MatchPrediction, MatchResult


def result_probabilities(
    results: list[MatchResult],
    home_team: str,
    away_team: str,
    knockout: bool,
) -> tuple[float, float, float]:
    total = len(results)
    home_wins = sum(result.goals_a > result.goals_b for result in results)
    away_wins = sum(result.goals_b > result.goals_a for result in results)
    draws = sum(result.goals_a == result.goals_b for result in results)

    return home_wins / total, draws / total, away_wins / total


def select_representative_score(
    score_matrix: list[list[float]],
    home_win_probability: float,
    draw_probability: float,
    away_win_probability: float,
    seed: int | str | None = None,
) -> tuple[int, int]:
    """Sample a representative score from an unchanged Poisson score matrix."""
    if not score_matrix or not all(score_matrix):
        raise ValueError("score_matrix must not be empty")
    if any(len(row) != len(score_matrix[0]) for row in score_matrix):
        raise ValueError("score_matrix rows must have equal length")
    if abs(home_win_probability + draw_probability + away_win_probability - 1.0) > 1e-6:
        raise ValueError("win/draw/loss probabilities must sum to one")

    scores = [
        (home_goals, away_goals)
        for home_goals, row in enumerate(score_matrix)
        for away_goals in range(len(row))
    ]
    weights = [probability for row in score_matrix for probability in row]
    if sum(weights) <= 0:
        raise ValueError("score_matrix must contain positive probability mass")

    return random.Random(seed).choices(scores, weights=weights, k=1)[0]


def average_goals(results: list[MatchResult], team: str) -> float:
    goals = [
        result.goals_a if result.team_a == team else result.goals_b
        for result in results
    ]
    return round(sum(goals) / len(goals), 4)


def predicted_winner_from_probabilities(
    home_team: str,
    away_team: str,
    home_win_probability: float,
    draw_probability: float,
    away_win_probability: float,
    allow_draw: bool,
) -> str | None:
    if allow_draw and draw_probability >= max(home_win_probability, away_win_probability):
        return None
    if home_win_probability >= away_win_probability:
        return home_team
    return away_team


def prediction_to_match_result(prediction: MatchPrediction) -> MatchResult:
    is_draw = prediction.predicted_home_goals == prediction.predicted_away_goals
    return MatchResult(
        team_a=prediction.home_team,
        team_b=prediction.away_team,
        goals_a=prediction.predicted_home_goals,
        goals_b=prediction.predicted_away_goals,
        winner=prediction.predicted_winner,
        is_draw=is_draw,
        decided_by=(
            "higher_win_probability_after_draw"
            if is_draw and prediction.predicted_winner
            else "draw" if is_draw else "regular_time"
        ),
        match_id=prediction.match_id,
    )
