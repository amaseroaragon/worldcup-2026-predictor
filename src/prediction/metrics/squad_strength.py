from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SquadStrengthRating:
    """Squad market value rating calculated on a logarithmic scale."""

    team: str
    squad_value: float
    squad_strength_rating: float


def load_squad_values(path: str | Path) -> dict[str, float]:
    """Load squad market values from a JSON file."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Squad values file does not exist: {config_path}")

    with config_path.open(encoding="utf-8") as file:
        data: Any = json.load(file)

    if not isinstance(data, dict) or not isinstance(data.get("teams"), dict):
        raise ValueError("Squad values config must contain a 'teams' object")

    squad_values: dict[str, float] = {}
    for team, value in data["teams"].items():
        if not isinstance(team, str):
            raise ValueError("Squad value team names must be strings")
        if not isinstance(value, int | float):
            raise ValueError(f"Squad value for {team} must be numeric")
        if value < 0:
            raise ValueError(f"Squad value for {team} must be non-negative")

        squad_values[team] = float(value)

    return squad_values


def build_squad_strength_ratings(
    squad_values: dict[str, float],
    *,
    min_rating: float = 0.85,
    max_rating: float = 1.15,
) -> dict[str, SquadStrengthRating]:
    """Build normalized squad strength ratings from market values.

    Values are transformed with ``log1p`` and compared with the global mean
    logarithmic value. The final rating is clipped to conservative bounds.
    """
    if min_rating <= 0 or max_rating <= 0:
        raise ValueError("rating bounds must be positive")

    if min_rating > max_rating:
        raise ValueError("min_rating must not exceed max_rating")

    if any(value < 0 for value in squad_values.values()):
        raise ValueError("squad values must be non-negative")

    if not squad_values:
        return {}

    log_values = {
        team: math.log1p(value)
        for team, value in squad_values.items()
    }
    mean_log_value = sum(log_values.values()) / len(log_values)

    ratings: dict[str, SquadStrengthRating] = {}
    for team, squad_value in squad_values.items():
        if mean_log_value == 0:
            raw_rating = 1.0
        else:
            raw_rating = log_values[team] / mean_log_value

        ratings[team] = SquadStrengthRating(
            team=team,
            squad_value=float(squad_value),
            squad_strength_rating=float(min(max(raw_rating, min_rating), max_rating)),
        )

    return ratings
