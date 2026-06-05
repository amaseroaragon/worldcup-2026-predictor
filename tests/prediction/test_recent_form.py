from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from src.prediction.metrics.recent_form import RecentFormRating, build_recent_form_ratings


def _team_a_results(points: list[int]) -> pd.DataFrame:
    rows = []
    for index, team_points in enumerate(points, start=1):
        if team_points == 3:
            home_score, away_score = 1, 0
        elif team_points == 1:
            home_score = away_score = 0
        else:
            home_score, away_score = 0, 1

        rows.append(
            {
                "date": f"2026-01-{index:02d}",
                "home_team": "A",
                "away_team": f"Opponent {index}",
                "home_score": home_score,
                "away_score": away_score,
            }
        )
    return pd.DataFrame(rows)


def test_build_recent_form_ratings_applies_linear_recency_weights():
    results = _team_a_results([0, 0, 0, 0, 3]).iloc[::-1]

    ratings = build_recent_form_ratings(results)

    expected_weighted_points_per_match = 15 / 15
    expected_form = 0.8 + 0.4 * (expected_weighted_points_per_match / 3)
    assert ratings["A"].form_5 == pytest.approx(expected_form)
    assert ratings["A"].form_10 is None
    assert ratings["A"].form_20 is None
    assert ratings["A"].matches_available == 5


def test_build_recent_form_ratings_calculates_all_windows_and_range():
    ratings = build_recent_form_ratings(_team_a_results([3] * 20))

    assert ratings["A"] == RecentFormRating("A", 1.2, 1.2, 1.2, 20)
    assert all(
        0.8 <= value <= 1.2
        for value in (ratings["A"].form_5, ratings["A"].form_10, ratings["A"].form_20)
    )


def test_build_recent_form_ratings_counts_home_and_away_results():
    results = pd.DataFrame(
        [
            {
                "date": f"2026-01-{index:02d}",
                "home_team": f"Opponent {index}",
                "away_team": "A",
                "home_score": 0,
                "away_score": 1,
            }
            for index in range(1, 6)
        ]
    )

    ratings = build_recent_form_ratings(results)

    assert ratings["A"].form_5 == pytest.approx(1.2)


def test_build_recent_form_ratings_returns_empty_mapping_for_empty_results():
    results = pd.DataFrame(columns=["date", "home_team", "away_team", "home_score", "away_score"])

    assert build_recent_form_ratings(results) == {}


def test_build_recent_form_ratings_rejects_missing_columns():
    with pytest.raises(ValueError, match="away_score"):
        build_recent_form_ratings(pd.DataFrame({"date": []}))


def test_recent_form_rating_is_frozen_and_validates_window():
    rating = RecentFormRating("A", 1.0, None, None, 5)

    assert rating.for_window(5) == 1.0
    with pytest.raises(ValueError, match="Unsupported"):
        rating.for_window(7)
    with pytest.raises(FrozenInstanceError):
        rating.form_5 = 1.2  # type: ignore[misc]
