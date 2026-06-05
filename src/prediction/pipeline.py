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
from src.prediction.settings import PATH_SETTINGS, PROJECT_ROOT, PathSettings
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
    groups_config: str | Path | None = None,
    group_matches_config: str | Path | None = None,
    knockouts_config: str | Path | None = None,
    third_place_combinations_config: str | Path | None = None,
    squad_values_config: str | Path | None = None,
    clean_results_path: str | Path | None = None,
    path_settings: PathSettings = PATH_SETTINGS,
    allow_missing_third_place_combinations: bool = False,
) -> PredictionInputs:
    """Load and derive the reusable inputs shared by prediction scripts."""

    ratings = load_ratings(path_settings.elo_rankings_path)
    results = pd.read_csv(clean_results_path or path_settings.clean_results_path)
    team_strength_ratings = build_team_strength_ratings(results)
    recent_form_ratings = build_recent_form_ratings(results)
    squad_values = load_squad_values(squad_values_config or path_settings.squad_values_path)
    squad_strength_ratings = build_squad_strength_ratings(squad_values)
    groups = load_groups_config(groups_config or path_settings.groups_path)
    group_matches = load_group_matches_config(
        group_matches_config or path_settings.group_matches_path
    )
    knockout_matches = load_knockouts_config(knockouts_config or path_settings.knockouts_path)
    third_place_combinations_path = (
        third_place_combinations_config or path_settings.third_place_combinations_path
    )
    if (
        allow_missing_third_place_combinations
        and not Path(third_place_combinations_path).exists()
    ):
        third_place_combinations = {}
    else:
        third_place_combinations = load_third_place_combinations_config(
            third_place_combinations_path
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
