from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.prediction.core.models import MatchPrediction, TournamentOutcome
from src.prediction.settings import (
    DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
    PREDICTIONS_OUTPUT_DIR,
    PROBABILITY_COLUMNS,
    PROBABILITY_VALUE_COLUMNS,
)

DEFAULT_WORLD_CUP_TEAM_METRICS_JSON_PATH = (
    PREDICTIONS_OUTPUT_DIR / "world_cup_team_metrics.json"
)
DEFAULT_GROUP_RESULTS_JSON_PATH = PREDICTIONS_OUTPUT_DIR / "group_results.json"


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


def export_world_cup_team_metrics(
    team_metrics: dict,
    groups: dict[str, list[str]],
    output_path: str | Path = DEFAULT_WORLD_CUP_TEAM_METRICS_JSON_PATH,
) -> dict:
    """Write team metrics filtered to the configured World Cup groups."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    group_by_team = {
        team: group
        for group, teams in groups.items()
        for team in teams
    }
    metrics_by_team = {
        record["team"]: record
        for record in team_metrics.get("teams", [])
    }
    records = []
    for team, group in group_by_team.items():
        if team not in metrics_by_team:
            raise ValueError(f"Missing team metrics for World Cup team: {team}")
        record = metrics_by_team[team]
        records.append(
            {
                "team": team,
                "group": group,
                "attack_rating": record.get("attack_rating"),
                "defense_rating": record.get("defense_rating"),
                "matches_used": record.get("matches_used"),
                "recent_form": record.get("recent_form"),
                "squad_strength": record.get("squad_strength"),
            }
        )

    payload = {
        "metadata": {
            "source": "team_metrics.json",
            "scope": "world_cup_2026_teams",
        },
        "teams": sorted(records, key=lambda record: (record["group"], record["team"])),
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return payload


def export_group_results(
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
    output_path: str | Path = DEFAULT_GROUP_RESULTS_JSON_PATH,
) -> dict:
    """Write aggregate group standings from Monte Carlo tournament outcomes."""

    if not outcomes:
        raise ValueError("outcomes must not be empty")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    totals = defaultdict(
        lambda: {
            "position": 0.0,
            "played": 0.0,
            "points": 0.0,
            "goals_for": 0.0,
            "goals_against": 0.0,
            "goal_difference": 0.0,
            "qualified": 0,
        }
    )
    for outcome in outcomes:
        for group, group_outcome in outcome.group_outcomes.items():
            for position, row in enumerate(group_outcome.standings, start=1):
                values = totals[(group, row.team)]
                values["position"] += position
                values["played"] += row.played
                values["points"] += row.points
                values["goals_for"] += row.goals_for
                values["goals_against"] += row.goals_against
                values["goal_difference"] += row.goal_difference
                values["qualified"] += int(row.team in outcome.round_of_32)

    simulations = len(outcomes)
    group_results = {}
    for group, teams in groups.items():
        records = []
        for team in teams:
            values = totals[(group, team)]
            records.append(
                {
                    "team": team,
                    "expected_position": values["position"] / simulations,
                    "expected_played": values["played"] / simulations,
                    "expected_points": values["points"] / simulations,
                    "expected_goals_for": values["goals_for"] / simulations,
                    "expected_goals_against": values["goals_against"] / simulations,
                    "expected_goal_difference": values["goal_difference"] / simulations,
                    "qualification_probability": values["qualified"] / simulations,
                }
            )

        records.sort(
            key=lambda record: (
                record["expected_position"],
                -record["expected_points"],
                -record["expected_goal_difference"],
                -record["expected_goals_for"],
                record["team"],
            )
        )
        group_results[group] = [
            {"position": position, **record}
            for position, record in enumerate(records, start=1)
        ]

    payload = {
        "metadata": {
            "source": "monte_carlo",
            "scope": "world_cup_2026_group_results",
            "simulations": simulations,
        },
        "groups": group_results,
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
