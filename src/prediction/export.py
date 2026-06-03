from __future__ import annotations

from pathlib import Path

import pandas as pd


PROBABILITY_COLUMNS = [
    "team",
    "champion_probability",
    "runner_up_probability",
    "semifinal_probability",
]


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
