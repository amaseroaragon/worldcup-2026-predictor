from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.prediction.core.models import MatchPrediction
from src.prediction.settings import (
    DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
    PROBABILITY_COLUMNS,
    PROBABILITY_VALUE_COLUMNS,
)


def probabilities_to_dataframe(probabilities: dict) -> pd.DataFrame:
    """Convert aggregate tournament probabilities into a sorted dataframe."""

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


def export_probabilities(
    probabilities: dict,
    output_path: str | Path = DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
) -> pd.DataFrame:
    """Write aggregate tournament probabilities to JSON."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = probabilities_to_dataframe(probabilities)
    rows = df.to_dict(orient="records")
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    return df


def export_match_predictions_json(
    predictions: list[MatchPrediction],
    output_path: str | Path = DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    metadata: dict | None = None,
) -> dict:
    """Write match predictions to a JSON file."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [asdict(prediction) for prediction in predictions]
    payload = {
        "metadata": metadata or {},
        "matches": rows,
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return payload


def validate_probability_output(df: pd.DataFrame) -> None:
    """Validate the exported probability dataframe contract."""

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
