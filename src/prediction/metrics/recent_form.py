from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


FORM_WINDOWS = (5, 10, 20)
REQUIRED_RESULT_COLUMNS = {
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
}


@dataclass(frozen=True)
class RecentFormRating:
    """Recent form ratings calculated from weighted match results."""

    team: str
    form_5: float | None
    form_10: float | None
    form_20: float | None
    matches_available: int

    def for_window(self, window: int) -> float | None:
        """Return the form rating for a supported match window."""
        if window not in FORM_WINDOWS:
            raise ValueError(f"Unsupported recent form window: {window}")
        return getattr(self, f"form_{window}")


def build_recent_form_ratings(results: pd.DataFrame) -> dict[str, RecentFormRating]:
    """Build recency-weighted form ratings for every team in the results."""
    missing_columns = REQUIRED_RESULT_COLUMNS - set(results.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required result columns: {missing}")

    if results.empty:
        return {}

    ordered_results = results.copy()
    ordered_results["_match_order"] = range(len(ordered_results))
    ordered_results["_parsed_date"] = pd.to_datetime(ordered_results["date"])
    ordered_results = ordered_results.sort_values(["_parsed_date", "_match_order"])

    team_points: dict[str, list[int]] = {}
    for row in ordered_results.itertuples(index=False):
        if row.home_score > row.away_score:
            home_points, away_points = 3, 0
        elif row.home_score < row.away_score:
            home_points, away_points = 0, 3
        else:
            home_points = away_points = 1

        team_points.setdefault(str(row.home_team), []).append(home_points)
        team_points.setdefault(str(row.away_team), []).append(away_points)

    return {
        team: RecentFormRating(
            team=team,
            form_5=_form_rating(points, 5),
            form_10=_form_rating(points, 10),
            form_20=_form_rating(points, 20),
            matches_available=len(points),
        )
        for team, points in team_points.items()
    }


def _form_rating(points: list[int], window: int) -> float | None:
    if len(points) < window:
        return None

    recent_points = points[-window:]
    weights = range(1, window + 1)
    weighted_points_per_match = sum(
        match_points * weight
        for match_points, weight in zip(recent_points, weights, strict=True)
    ) / sum(weights)
    raw_form = weighted_points_per_match / 3
    form_rating = 0.8 + 0.4 * raw_form
    return min(max(form_rating, 0.8), 1.2)
