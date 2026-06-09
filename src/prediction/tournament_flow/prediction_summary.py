from __future__ import annotations

from src.prediction.core.models import MatchPrediction, MatchResult
from src.prediction.settings import DRAW_COMPETITIVE_MARGIN


HOME_WIN = "home_win"
DRAW = "draw"
AWAY_WIN = "away_win"


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


def select_displayed_outcome(
    home_win_probability: float,
    draw_probability: float,
    away_win_probability: float,
    draw_competitive_margin: float = DRAW_COMPETITIVE_MARGIN,
) -> str:
    """Return a deterministic outcome, allowing statistically competitive draws."""
    probabilities = (home_win_probability, draw_probability, away_win_probability)
    if any(probability < 0 or probability > 1 for probability in probabilities):
        raise ValueError("win/draw/loss probabilities must be between zero and one")
    if draw_competitive_margin < 0:
        raise ValueError("draw_competitive_margin must be non-negative")

    max_win_probability = max(home_win_probability, away_win_probability)
    if draw_probability >= max_win_probability - draw_competitive_margin:
        return DRAW
    return HOME_WIN if home_win_probability >= away_win_probability else AWAY_WIN


def is_competitive_draw_selected(
    home_win_probability: float,
    draw_probability: float,
    away_win_probability: float,
    draw_competitive_margin: float = DRAW_COMPETITIVE_MARGIN,
) -> bool:
    """Return whether the margin promotes draw over a higher win probability."""
    max_win_probability = max(home_win_probability, away_win_probability)
    return (
        draw_probability < max_win_probability
        and select_displayed_outcome(
            home_win_probability,
            draw_probability,
            away_win_probability,
            draw_competitive_margin,
        )
        == DRAW
    )


def select_most_likely_score_for_outcome(
    score_matrix: list[list[float]],
    outcome: str,
) -> tuple[int, int]:
    """Return the highest-probability score compatible with an outcome class."""
    _probability, home_goals, away_goals = ranked_scores_for_outcome(
        score_matrix,
        outcome,
    )[0]
    return home_goals, away_goals


def ranked_scores_for_outcome(
    score_matrix: list[list[float]],
    outcome: str,
) -> list[tuple[float, int, int]]:
    """Return compatible scores ordered from most to least likely."""
    if not score_matrix or not all(score_matrix):
        raise ValueError("score_matrix must not be empty")
    if any(len(row) != len(score_matrix[0]) for row in score_matrix):
        raise ValueError("score_matrix rows must have equal length")
    if outcome not in {HOME_WIN, DRAW, AWAY_WIN}:
        raise ValueError(f"Unknown outcome: {outcome}")

    candidates = [
        (probability, home_goals, away_goals)
        for home_goals, row in enumerate(score_matrix)
        for away_goals, probability in enumerate(row)
        if (
            (outcome == HOME_WIN and home_goals > away_goals)
            or (outcome == DRAW and home_goals == away_goals)
            or (outcome == AWAY_WIN and away_goals > home_goals)
        )
    ]
    if not candidates or max(probability for probability, _home, _away in candidates) <= 0:
        raise ValueError(f"score_matrix has no positive probability mass for {outcome}")

    return sorted(
        candidates,
        key=lambda candidate: (-candidate[0], candidate[1] + candidate[2]),
    )


def score_contradicts_displayed_outcome(
    home_team: str,
    away_team: str,
    home_goals: int,
    away_goals: int,
    winner: str | None,
    advanced_by: str | None,
    home_win_probability: float,
    draw_probability: float,
    away_win_probability: float,
) -> bool:
    """Return whether score/winner contradict the deterministic displayed outcome."""
    outcome = select_displayed_outcome(
        home_win_probability,
        draw_probability,
        away_win_probability,
    )
    if outcome == HOME_WIN:
        return home_goals <= away_goals or winner != home_team or advanced_by == "higher_win_probability_after_draw"
    if outcome == AWAY_WIN:
        return away_goals <= home_goals or winner != away_team or advanced_by == "higher_win_probability_after_draw"

    expected_draw_winner = (
        home_team if home_win_probability >= away_win_probability else away_team
    )
    if advanced_by is None:
        return home_goals != away_goals or winner is not None
    return (
        home_goals != away_goals
        or winner != expected_draw_winner
        or advanced_by != "higher_win_probability_after_draw"
    )


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
