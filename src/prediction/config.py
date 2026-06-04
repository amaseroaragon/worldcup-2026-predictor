from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORLD_CUP_2026_GROUPS_PATH = PROJECT_ROOT / "data/external/groups.json"
DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH = PROJECT_ROOT / "data/external/knockouts.json"
DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH = (
    PROJECT_ROOT / "data/external/third_place_combinations.json"
)
TEAMS_PER_GROUP = 4
USE_RECENT_FORM = True
RECENT_FORM_WEIGHT = 0.15
RECENT_FORM_PRIMARY_WINDOW = 10


def load_groups_config(path: str | Path) -> dict[str, list[str]]:
    """Load and validate World Cup group configuration."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Groups config file does not exist: {config_path}")

    with config_path.open(encoding="utf-8") as file:
        data: Any = json.load(file)

    if not isinstance(data, dict) or "groups" not in data:
        raise ValueError("Groups config must contain a 'groups' key")

    groups = data["groups"]
    if not isinstance(groups, dict):
        raise ValueError("Groups config 'groups' value must be an object")

    loaded_groups: dict[str, list[str]] = {}
    for group, teams in groups.items():
        if not isinstance(group, str):
            raise ValueError("Group names must be strings")
        if not isinstance(teams, list) or len(teams) != TEAMS_PER_GROUP:
            raise ValueError(f"Group {group} must have exactly {TEAMS_PER_GROUP} teams")
        if not all(isinstance(team, str) for team in teams):
            raise ValueError(f"Group {group} must contain only string team names")

        loaded_groups[group] = teams

    return loaded_groups


def load_knockouts_config(path: str | Path) -> list[dict[str, str]]:
    """Load and validate knockout bracket configuration."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Knockouts config file does not exist: {config_path}")

    with config_path.open(encoding="utf-8") as file:
        data: Any = json.load(file)

    if not isinstance(data, dict) or "matches" not in data:
        raise ValueError("Knockouts config must contain a 'matches' key")

    matches = data["matches"]
    if not isinstance(matches, list):
        raise ValueError("Knockouts config 'matches' value must be a list")

    loaded_matches: list[dict[str, str]] = []
    required_fields = {"match_id", "round", "home", "away"}
    for index, match in enumerate(matches, start=1):
        if not isinstance(match, dict):
            raise ValueError(f"Knockout match {index} must be an object")

        missing_fields = required_fields - set(match)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Knockout match {index} is missing required fields: {missing}")

        if not all(isinstance(match[field], str) for field in required_fields):
            raise ValueError(f"Knockout match {index} fields must be strings")

        loaded_matches.append(
            {
                "match_id": match["match_id"],
                "round": match["round"],
                "home": match["home"],
                "away": match["away"],
            }
        )

    return loaded_matches


def load_third_place_combinations_config(path: str | Path) -> dict[str, dict[str, str]]:
    """Load valid third-place placeholder combinations."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Third-place combinations config file does not exist: {config_path}")

    with config_path.open(encoding="utf-8") as file:
        data: Any = json.load(file)

    if not isinstance(data, dict) or "by_best_thirds" not in data:
        raise ValueError("Third-place combinations config must contain a 'by_best_thirds' key")

    combinations = data["by_best_thirds"]
    if not isinstance(combinations, dict):
        raise ValueError("Third-place combinations 'by_best_thirds' value must be an object")

    loaded_combinations: dict[str, dict[str, str]] = {}
    for key, value in combinations.items():
        if not isinstance(key, str):
            raise ValueError("Third-place combination keys must be strings")
        if not isinstance(value, dict) or not isinstance(value.get("placeholder_resolution"), dict):
            raise ValueError(f"Third-place combination {key} must define placeholder_resolution")

        placeholder_resolution = value["placeholder_resolution"]
        if not all(
            isinstance(placeholder, str) and isinstance(resolution, str)
            for placeholder, resolution in placeholder_resolution.items()
        ):
            raise ValueError(f"Third-place combination {key} placeholder resolutions must be strings")

        loaded_combinations[key] = dict(placeholder_resolution)

    return loaded_combinations
