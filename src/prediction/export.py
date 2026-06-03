from __future__ import annotations

from pathlib import Path

import pandas as pd


PROBABILITY_COLUMNS = [
    "team",
    "champion_probability",
    "runner_up_probability",
    "semifinal_probability",
]
PROBABILITY_VALUE_COLUMNS = PROBABILITY_COLUMNS[1:]


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
