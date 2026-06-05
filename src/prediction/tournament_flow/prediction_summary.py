from __future__ import annotations

from collections import Counter

from src.prediction.core.models import MatchPrediction, MatchResult


def result_probabilities(
    results: list[MatchResult],
    home_team: str,
    away_team: str,
    knockout: bool,
) -> tuple[float, float, float]:
    total = len(results)
    home_wins = sum(result.winner == home_team for result in results)
    away_wins = sum(result.winner == away_team for result in results)
    draws = 0 if knockout else sum(result.winner is None for result in results)

    return home_wins / total, draws / total, away_wins / total


def most_common_score(
    results: list[MatchResult],
    predicted_winner: str | None,
) -> tuple[int, int]:
    matching_results = [
        result for result in results
        if result.winner == predicted_winner
    ]
    score_results = matching_results or results
    return Counter(
        (result.goals_a, result.goals_b)
        for result in score_results
    ).most_common(1)[0][0]


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
        is_draw=prediction.predicted_winner is None,
        decided_by="tiebreaker" if is_draw and prediction.predicted_winner else "regular_time",
        match_id=prediction.match_id,
    )
