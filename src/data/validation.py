from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.prediction.config import (
    load_group_matches_config,
    load_groups_config,
    load_knockouts_config,
    load_third_place_combinations_config,
)
from src.prediction.ratings import REQUIRED_RATING_COLUMNS
from src.prediction.settings import MATCHES_PER_GROUP
from src.prediction.metrics.squad_strength import load_squad_values


CLEAN_RESULTS_REQUIRED_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
    "neutral",
]


def validate_clean_results_dataframe(df: pd.DataFrame) -> None:
    """Validate the clean historical results contract."""

    missing_columns = set(CLEAN_RESULTS_REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing clean results columns: {missing}")

    critical_nulls = df[CLEAN_RESULTS_REQUIRED_COLUMNS].isnull().sum()
    if critical_nulls.sum() > 0:
        raise ValueError(f"Critical null values found:\n{critical_nulls}")

    if (df["home_score"] < 0).any() or (df["away_score"] < 0).any():
        raise ValueError("Negative scores found.")

    if (df["home_team"] == df["away_team"]).any():
        raise ValueError("Some matches have the same home and away team.")


def validate_world_cup_external_configs(
    *,
    groups_path: str | Path,
    group_matches_path: str | Path,
    knockouts_path: str | Path,
    third_place_combinations_path: str | Path,
    squad_values_path: str | Path,
    elo_rankings_path: str | Path,
) -> None:
    """Validate the cross-file contract for the World Cup prediction inputs."""

    groups = load_groups_config(groups_path)
    group_matches = load_group_matches_config(group_matches_path)
    knockouts = load_knockouts_config(knockouts_path)
    third_place_combinations = load_third_place_combinations_config(
        third_place_combinations_path
    )
    squad_values = load_squad_values(squad_values_path)
    rankings = pd.read_csv(elo_rankings_path)

    missing_rating_columns = REQUIRED_RATING_COLUMNS - set(rankings.columns)
    if missing_rating_columns:
        missing = ", ".join(sorted(missing_rating_columns))
        raise ValueError(f"Missing Elo ranking columns: {missing}")

    teams = {team for group_teams in groups.values() for team in group_teams}
    if len(teams) != sum(len(group_teams) for group_teams in groups.values()):
        raise ValueError("Groups config contains duplicate teams")

    _validate_group_matches_cover_groups(groups, group_matches)
    _validate_knockout_match_ids(knockouts)
    _validate_third_place_combinations(third_place_combinations)

    missing_squad_values = teams - set(squad_values)
    if missing_squad_values:
        missing = ", ".join(sorted(missing_squad_values))
        raise ValueError(f"Missing squad values for World Cup teams: {missing}")

    missing_elo_ratings = teams - set(rankings["team"])
    if missing_elo_ratings:
        missing = ", ".join(sorted(missing_elo_ratings))
        raise ValueError(f"Missing Elo ratings for World Cup teams: {missing}")


def validate_json_file(path: str | Path) -> Any:
    """Load a JSON file and fail with a clear file-specific message."""

    json_path = Path(path)
    try:
        with json_path.open(encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON file {json_path}: {exc}") from exc


def _validate_group_matches_cover_groups(
    groups: dict[str, list[str]],
    group_matches: list[dict[str, str | int]],
) -> None:
    counts = {
        group: sum(match["group"] == group for match in group_matches)
        for group in groups
    }
    invalid_counts = {
        group: count
        for group, count in counts.items()
        if count != MATCHES_PER_GROUP
    }
    if invalid_counts:
        raise ValueError(f"Invalid group match counts: {invalid_counts}")

    seen_match_ids = set()
    for match in group_matches:
        match_id = str(match["match_id"])
        if match_id in seen_match_ids:
            raise ValueError(f"Duplicate group match id: {match_id}")
        seen_match_ids.add(match_id)

        group = str(match["group"])
        home = str(match["home"])
        away = str(match["away"])
        if group not in groups:
            raise ValueError(f"Unknown group in group match: {group}")
        if home not in groups[group] or away not in groups[group]:
            raise ValueError(f"Group match {match_id} contains team outside group {group}")
        if home == away:
            raise ValueError(f"Group match {match_id} has the same home and away team")


def _validate_knockout_match_ids(knockouts: list[dict[str, str]]) -> None:
    seen_match_ids = set()
    for match in knockouts:
        match_id = match["match_id"]
        if match_id in seen_match_ids:
            raise ValueError(f"Duplicate knockout match id: {match_id}")
        seen_match_ids.add(match_id)


def _validate_third_place_combinations(
    third_place_combinations: dict[str, dict[str, str]],
) -> None:
    for best_thirds, placeholder_resolution in third_place_combinations.items():
        if len(best_thirds) != 8:
            raise ValueError(f"Third-place key must contain 8 groups: {best_thirds}")
        if "".join(sorted(best_thirds)) != best_thirds:
            raise ValueError(f"Third-place key must be sorted: {best_thirds}")
        for placeholder, resolution in placeholder_resolution.items():
            if not placeholder.startswith("3") or not resolution.startswith("3"):
                raise ValueError(
                    f"Invalid third-place placeholder mapping: {placeholder} -> {resolution}"
                )
