from __future__ import annotations

from src.prediction.core.models import MatchPrediction, MatchResult
from src.prediction.core.probabilities import elo_win_draw_loss_probs


def build_match_predictions(
    match_results: list[MatchResult],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]] | None = None,
) -> list[MatchPrediction]:
    """Build persistable match prediction records from simulated match results."""

    knockout_rounds = {
        match["match_id"]: match["round"]
        for match in knockout_matches or []
    }
    return [
        _build_match_prediction(result, ratings, knockout_rounds)
        for result in match_results
    ]


def _build_match_prediction(
    result: MatchResult,
    ratings: dict[str, float],
    knockout_rounds: dict[str, str],
) -> MatchPrediction:
    missing_ratings = [
        team for team in (result.team_a, result.team_b) if team not in ratings
    ]
    if missing_ratings:
        missing = ", ".join(missing_ratings)
        raise ValueError(f"Missing Elo rating for: {missing}")

    home_elo = ratings[result.team_a]
    away_elo = ratings[result.team_b]
    home_win_probability, draw_probability, away_win_probability = elo_win_draw_loss_probs(
        home_elo,
        away_elo,
    )
    stage, group, round_name = _match_metadata(result.match_id, knockout_rounds)

    return MatchPrediction(
        match_id=result.match_id or "",
        stage=stage,
        group=group,
        round=round_name,
        home_team=result.team_a,
        away_team=result.team_b,
        predicted_home_goals=result.goals_a,
        predicted_away_goals=result.goals_b,
        predicted_winner=result.winner,
        home_win_probability=home_win_probability,
        draw_probability=draw_probability,
        away_win_probability=away_win_probability,
    )


def _match_metadata(
    match_id: str | None,
    knockout_rounds: dict[str, str],
) -> tuple[str, str | None, str | None]:
    if match_id is None:
        return "unknown", None, None

    if match_id.startswith("group_"):
        parts = match_id.split("_")
        group = parts[1] if len(parts) >= 3 else None
        return "group", group, None

    round_name = knockout_rounds.get(match_id)
    if round_name is not None:
        return round_name, None, round_name

    return "knockout", None, None
