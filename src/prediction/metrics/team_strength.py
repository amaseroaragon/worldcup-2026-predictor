from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.prediction.metrics.recent_form import RecentFormRating
from src.prediction.metrics.squad_strength import SquadStrengthRating
from src.prediction.settings import (
    DEFAULT_TEAM_METRICS_PATH,
    METRICS_VERSION,
    MODEL_WEIGHTS,
    SQUAD_VALUE_UNIT,
    SQUAD_VALUES_SOURCE,
    TEAM_STRENGTH_MAX_RATING,
    TEAM_STRENGTH_MIN_MATCHES,
    TEAM_STRENGTH_MIN_RATING,
    TEAM_STRENGTH_RECENT_MATCHES,
    TEAM_STRENGTH_SHRINK_FACTOR,
)


REQUIRED_RESULT_COLUMNS = {
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
}


@dataclass(frozen=True)
class TeamStrengthRating:
    """Attack and defense ratings calculated from historical results."""

    team: str
    attack_rating: float
    defense_rating: float
    matches_used: int


def build_team_strength_ratings(
    results: pd.DataFrame,
    *,
    elo_ratings: dict[str, float] | None = None,
    recent_matches: int | None = TEAM_STRENGTH_RECENT_MATCHES,
    min_matches: int = TEAM_STRENGTH_MIN_MATCHES,
    shrink_factor: float = TEAM_STRENGTH_SHRINK_FACTOR,
    min_rating: float = TEAM_STRENGTH_MIN_RATING,
    max_rating: float = TEAM_STRENGTH_MAX_RATING,
) -> dict[str, TeamStrengthRating]:
    """Build attack and defense ratings from normalized historical results.

    When Elo ratings are supplied, actual goals are compared with the goals
    expected against each opponent. This adjusts schedule strength while
    preserving the intuitive interpretation that 1.0 is neutral. Raw ratings
    are partially regressed toward 1.0 before safety clipping.
    """
    missing_columns = REQUIRED_RESULT_COLUMNS - set(results.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required result columns: {missing}")

    if min_matches < 0:
        raise ValueError("min_matches must be non-negative")

    if recent_matches is not None and recent_matches <= 0:
        raise ValueError("recent_matches must be positive")

    if min_rating <= 0 or max_rating <= 0:
        raise ValueError("rating bounds must be positive")

    if min_rating > max_rating:
        raise ValueError("min_rating must not exceed max_rating")

    if not 0 <= shrink_factor <= 1:
        raise ValueError("shrink_factor must be between 0 and 1")

    if results.empty:
        return {}

    ordered_results = results.copy()
    ordered_results["_match_order"] = range(len(ordered_results))
    ordered_results["_parsed_date"] = pd.to_datetime(ordered_results["date"])

    home_results = ordered_results.loc[
        :,
        [
            "_parsed_date",
            "_match_order",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        ],
    ].rename(
        columns={
            "home_team": "team",
            "away_team": "opponent",
            "home_score": "goals_scored",
            "away_score": "goals_conceded",
        }
    )
    away_results = ordered_results.loc[
        :,
        [
            "_parsed_date",
            "_match_order",
            "away_team",
            "home_team",
            "away_score",
            "home_score",
        ],
    ].rename(
        columns={
            "away_team": "team",
            "home_team": "opponent",
            "away_score": "goals_scored",
            "home_score": "goals_conceded",
        }
    )
    team_results = pd.concat([home_results, away_results], ignore_index=True)
    team_results = team_results.sort_values(["team", "_parsed_date", "_match_order"])
    if recent_matches is not None:
        team_results = team_results.groupby("team", sort=False).tail(recent_matches)

    team_stats = team_results.groupby("team", sort=False).agg(
        matches_played=("team", "size"),
        goals_scored=("goals_scored", "sum"),
        goals_conceded=("goals_conceded", "sum"),
    )
    global_goals_per_team_match = team_stats["goals_scored"].sum() / team_stats["matches_played"].sum()
    expected_stats = None
    if elo_ratings:
        team_results["expected_goals_scored"] = team_results.apply(
            lambda row: _elo_expected_goals(
                str(row["team"]),
                str(row["opponent"]),
                elo_ratings,
            ),
            axis=1,
        )
        team_results["expected_goals_conceded"] = team_results.apply(
            lambda row: _elo_expected_goals(
                str(row["opponent"]),
                str(row["team"]),
                elo_ratings,
            ),
            axis=1,
        )
        expected_stats = team_results.groupby("team", sort=False).agg(
            expected_goals_scored=("expected_goals_scored", "sum"),
            expected_goals_conceded=("expected_goals_conceded", "sum"),
        )

    ratings: dict[str, TeamStrengthRating] = {}
    for team, stats in team_stats.iterrows():
        matches_played = int(stats["matches_played"])
        if matches_played < min_matches:
            continue

        if expected_stats is not None:
            expected = expected_stats.loc[team]
            attack_raw = (
                stats["goals_scored"] / expected["expected_goals_scored"]
                if expected["expected_goals_scored"] > 0
                else 1.0
            )
            defense_raw = (
                stats["goals_conceded"] / expected["expected_goals_conceded"]
                if expected["expected_goals_conceded"] > 0
                else 1.0
            )
        elif global_goals_per_team_match == 0:
            attack_raw = defense_raw = 1.0
        else:
            attack_raw = (stats["goals_scored"] / matches_played) / global_goals_per_team_match
            defense_raw = (stats["goals_conceded"] / matches_played) / global_goals_per_team_match

        attack_rating = 1.0 + shrink_factor * (attack_raw - 1.0)
        defense_rating = 1.0 + shrink_factor * (defense_raw - 1.0)

        ratings[str(team)] = TeamStrengthRating(
            team=str(team),
            attack_rating=float(min(max(attack_rating, min_rating), max_rating)),
            defense_rating=float(min(max(defense_rating, min_rating), max_rating)),
            matches_used=matches_played,
        )

    return ratings


def _elo_expected_goals(
    team: str,
    opponent: str,
    elo_ratings: dict[str, float],
) -> float:
    """Return a neutral expected-goals baseline conditioned on Elo strength."""
    elo_diff = elo_ratings.get(team, 1500.0) - elo_ratings.get(opponent, 1500.0)
    return MODEL_WEIGHTS.base_goals * math.exp(MODEL_WEIGHTS.elo_sensitivity * elo_diff)


def team_strength_ratings_to_records(
    ratings: dict[str, TeamStrengthRating],
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
) -> list[dict[str, object]]:
    """Convert team strength ratings into sorted, JSON-ready metric records."""
    records = []
    for rating in sorted(ratings.values(), key=lambda rating: rating.team):
        recent_form = recent_form_ratings.get(rating.team) if recent_form_ratings else None
        squad_strength = (
            squad_strength_ratings.get(rating.team) if squad_strength_ratings else None
        )
        records.append(
            {
                "team": rating.team,
                "attack_rating": rating.attack_rating,
                "defense_rating": rating.defense_rating,
                "matches_used": rating.matches_used,
                "recent_form": {
                    "form_5": recent_form.form_5 if recent_form else None,
                    "form_10": recent_form.form_10 if recent_form else None,
                    "form_20": recent_form.form_20 if recent_form else None,
                    "matches_available": recent_form.matches_available if recent_form else 0,
                },
                "squad_strength": {
                    "squad_value": squad_strength.squad_value,
                    "squad_strength_rating": squad_strength.squad_strength_rating,
                }
                if squad_strength
                else None,
            }
        )
    return records


def export_team_metrics(
    ratings: dict[str, TeamStrengthRating],
    output_path: str | Path = DEFAULT_TEAM_METRICS_PATH,
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
    squad_values_source: str = SQUAD_VALUES_SOURCE,
) -> dict[str, object]:
    """Export current team metrics to an extensible JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metrics_version": METRICS_VERSION,
        "squad_values_source": squad_values_source,
        "squad_value_unit": SQUAD_VALUE_UNIT,
        "teams": team_strength_ratings_to_records(
            ratings,
            recent_form_ratings,
            squad_strength_ratings,
        ),
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return payload
