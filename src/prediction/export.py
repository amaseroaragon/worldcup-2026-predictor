from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.prediction.models import MatchPrediction, MatchResult
from src.prediction.probabilities import elo_win_draw_loss_probs


PROBABILITY_COLUMNS = [
    "team",
    "champion_probability",
    "runner_up_probability",
    "semifinal_probability",
]
PROBABILITY_VALUE_COLUMNS = PROBABILITY_COLUMNS[1:]
DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH = Path(
    "outputs/predictions/tournament_predictions.json"
)


def probabilities_to_dataframe(probabilities: dict) -> pd.DataFrame:
    rows = [
        {
            "team": team,
            "champion_probability": values["champion"],
            "runner_up_probability": values["runner_up"],
            "semifinal_probability": values["semifinal"],
        }
        for team, values in probabilities.items()
    ]

    return (
        pd.DataFrame(rows, columns=PROBABILITY_COLUMNS)
        .sort_values("champion_probability", ascending=False)
        .reset_index(drop=True)
    )


def export_probabilities(probabilities: dict, output_path: str | Path) -> pd.DataFrame:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = probabilities_to_dataframe(probabilities)
    df.to_csv(output_path, index=False)

    return df


def build_match_predictions(
    match_results: list[MatchResult],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]] | None = None,
) -> list[MatchPrediction]:
    knockout_rounds = {
        match["match_id"]: match["round"]
        for match in knockout_matches or []
    }
    return [
        _build_match_prediction(result, ratings, knockout_rounds)
        for result in match_results
    ]


def export_match_predictions_json(
    predictions: list[MatchPrediction],
    output_path: str | Path = DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
) -> list[dict]:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [asdict(prediction) for prediction in predictions]
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    return rows


def validate_probability_output(df: pd.DataFrame) -> None:
    missing_columns = set(PROBABILITY_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing probability output columns: {missing}")

    if df.empty:
        raise ValueError("Probability output is empty")

    null_counts = df[PROBABILITY_COLUMNS].isna().sum()
    invalid_nulls = null_counts[null_counts > 0]
    if not invalid_nulls.empty:
        raise ValueError(f"Probability output contains null values:\n{invalid_nulls}")

    for column in PROBABILITY_VALUE_COLUMNS:
        if not df[column].between(0, 1).all():
            raise ValueError(f"{column} must contain values between 0 and 1")

    champion_probability_sum = df["champion_probability"].sum()
    if abs(champion_probability_sum - 1.0) > 1e-9:
        raise ValueError("Champion probabilities must sum to 1")


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
