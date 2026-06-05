from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.prediction.metrics.recent_form import RecentFormRating
from src.prediction.metrics.squad_strength import SquadStrengthRating
from src.prediction.settings import (
    DEFAULT_TEAM_METRICS_PATH,
    METRICS_VERSION,
    SQUAD_VALUE_UNIT,
    SQUAD_VALUES_SOURCE,
    TEAM_STRENGTH_MAX_RATING,
    TEAM_STRENGTH_MIN_MATCHES,
    TEAM_STRENGTH_MIN_RATING,
    TEAM_STRENGTH_RECENT_MATCHES,
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
    recent_matches: int | None = TEAM_STRENGTH_RECENT_MATCHES,
    min_matches: int = TEAM_STRENGTH_MIN_MATCHES,
    min_rating: float = TEAM_STRENGTH_MIN_RATING,
    max_rating: float = TEAM_STRENGTH_MAX_RATING,
) -> dict[str, TeamStrengthRating]:
    """Build attack and defense ratings from normalized historical results.

    Ratings compare each team's goals scored and conceded per match with the
    global goals-per-team-match average. By default, each team is measured on
    its most recent matches in the provided dataset. Teams below
    ``min_matches`` are excluded, and final ratings are clipped to the
    configured bounds.
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
            "home_score",
            "away_score",
        ],
    ].rename(
        columns={
            "home_team": "team",
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
            "away_score",
            "home_score",
        ],
    ].rename(
        columns={
            "away_team": "team",
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

    ratings: dict[str, TeamStrengthRating] = {}
    for team, stats in team_stats.iterrows():
        matches_played = int(stats["matches_played"])
        if matches_played < min_matches:
            continue

        if global_goals_per_team_match == 0:
            attack_rating = defense_rating = 1.0
        else:
            attack_rating = (stats["goals_scored"] / matches_played) / global_goals_per_team_match
            defense_rating = (stats["goals_conceded"] / matches_played) / global_goals_per_team_match

        ratings[str(team)] = TeamStrengthRating(
            team=str(team),
            attack_rating=float(min(max(attack_rating, min_rating), max_rating)),
            defense_rating=float(min(max(defense_rating, min_rating), max_rating)),
            matches_used=matches_played,
        )

    return ratings


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
