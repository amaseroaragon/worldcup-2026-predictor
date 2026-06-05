from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.prediction.config import (
    load_group_matches_config,
    load_groups_config,
    load_knockouts_config,
    load_third_place_combinations_config,
)
from src.prediction.ratings import load_ratings
from src.prediction.metrics.recent_form import RecentFormRating, build_recent_form_ratings
from src.prediction.settings import DEFAULT_CLEAN_RESULTS_PATH, PROJECT_ROOT
from src.prediction.metrics.squad_strength import (
    SquadStrengthRating,
    build_squad_strength_ratings,
    load_squad_values,
)
from src.prediction.metrics.team_strength import TeamStrengthRating, build_team_strength_ratings


@dataclass(frozen=True)
class PredictionInputs:
    ratings: dict[str, float]
    results: pd.DataFrame
    team_strength_ratings: dict[str, TeamStrengthRating]
    recent_form_ratings: dict[str, RecentFormRating]
    squad_strength_ratings: dict[str, SquadStrengthRating]
    groups: dict[str, list[str]]
    group_matches: list[dict[str, str | int]]
    knockout_matches: list[dict[str, str]]
    third_place_combinations: dict[str, dict[str, str]]


def load_prediction_inputs(
    *,
    groups_config: str | Path,
    group_matches_config: str | Path,
    knockouts_config: str | Path,
    third_place_combinations_config: str | Path,
    squad_values_config: str | Path,
    clean_results_path: str | Path = DEFAULT_CLEAN_RESULTS_PATH,
) -> PredictionInputs:
    """Load and derive the reusable inputs shared by prediction scripts."""

    ratings = load_ratings()
    results = pd.read_csv(clean_results_path)
    team_strength_ratings = build_team_strength_ratings(results)
    recent_form_ratings = build_recent_form_ratings(results)
    squad_values = load_squad_values(squad_values_config)
    squad_strength_ratings = build_squad_strength_ratings(squad_values)
    groups = load_groups_config(groups_config)
    group_matches = load_group_matches_config(group_matches_config)
    knockout_matches = load_knockouts_config(knockouts_config)
    third_place_combinations = load_third_place_combinations_config(
        third_place_combinations_config
    )

    return PredictionInputs(
        ratings=ratings,
        results=results,
        team_strength_ratings=team_strength_ratings,
        recent_form_ratings=recent_form_ratings,
        squad_strength_ratings=squad_strength_ratings,
        groups=groups,
        group_matches=group_matches,
        knockout_matches=knockout_matches,
        third_place_combinations=third_place_combinations,
    )


def path_relative_to_project(path: Path) -> str:
    """Return a stable project-relative path when possible."""

    return str(path.relative_to(PROJECT_ROOT)) if path.is_relative_to(PROJECT_ROOT) else str(path)
