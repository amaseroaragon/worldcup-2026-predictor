import json
from dataclasses import FrozenInstanceError

import pandas as pd
import pytest

from src.prediction.recent_form import RecentFormRating
from src.prediction.squad_strength import SquadStrengthRating
from src.prediction.team_strength import (
    METRICS_VERSION,
    TeamStrengthRating,
    build_team_strength_ratings,
    export_team_metrics,
    team_strength_ratings_to_records,
)


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": "2017-06-01",
                "home_team": "A",
                "away_team": "B",
                "home_score": 10,
                "away_score": 0,
            },
            {
                "date": "2018-06-01",
                "home_team": "A",
                "away_team": "B",
                "home_score": 2,
                "away_score": 0,
            },
            {
                "date": "2019-06-01",
                "home_team": "B",
                "away_team": "A",
                "home_score": 1,
                "away_score": 1,
            },
        ]
    )


def test_build_team_strength_ratings_calculates_attack_and_defense_for_both_venues():
    ratings = build_team_strength_ratings(
        _results(),
        start_year=2018,
        min_matches=2,
        min_rating=0.01,
        max_rating=10.0,
    )

    assert ratings["A"] == TeamStrengthRating(
        team="A",
        attack_rating=1.5,
        defense_rating=0.5,
        matches_used=2,
    )
    assert ratings["B"] == TeamStrengthRating(
        team="B",
        attack_rating=0.5,
        defense_rating=1.5,
        matches_used=2,
    )


def test_build_team_strength_ratings_can_include_results_before_default_start_year():
    ratings = build_team_strength_ratings(
        _results(),
        start_year=None,
        min_matches=3,
        min_rating=0.01,
        max_rating=10.0,
    )

    assert ratings["A"].matches_used == 3
    assert ratings["B"].matches_used == 3


def test_build_team_strength_ratings_excludes_teams_below_minimum_matches():
    ratings = build_team_strength_ratings(_results(), start_year=2018, min_matches=3)

    assert ratings == {}


def test_build_team_strength_ratings_clips_extreme_ratings():
    ratings = build_team_strength_ratings(_results(), start_year=2018, min_matches=2)

    assert ratings["A"].attack_rating == 1.45
    assert ratings["A"].defense_rating == 0.65
    assert ratings["B"].attack_rating == 0.65
    assert ratings["B"].defense_rating == 1.45


def test_build_team_strength_ratings_returns_empty_mapping_without_filtered_results():
    ratings = build_team_strength_ratings(_results(), start_year=2020)

    assert ratings == {}


def test_build_team_strength_ratings_uses_neutral_ratings_when_no_goals_were_scored():
    results = pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "home_team": "A",
                "away_team": "B",
                "home_score": 0,
                "away_score": 0,
            }
        ]
    )

    ratings = build_team_strength_ratings(results, min_matches=1)

    assert ratings["A"].attack_rating == 1.0
    assert ratings["A"].defense_rating == 1.0
    assert ratings["B"].attack_rating == 1.0
    assert ratings["B"].defense_rating == 1.0


def test_team_strength_rating_is_frozen():
    rating = TeamStrengthRating("A", 1.0, 1.0, 5)

    with pytest.raises(FrozenInstanceError):
        rating.attack_rating = 1.2  # type: ignore[misc]


def test_build_team_strength_ratings_rejects_missing_columns():
    with pytest.raises(ValueError, match="away_score"):
        build_team_strength_ratings(pd.DataFrame({"date": []}))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"min_matches": -1}, "min_matches"),
        ({"min_rating": 0.0}, "rating bounds"),
        ({"min_rating": 2.0, "max_rating": 1.0}, "min_rating"),
    ],
)
def test_build_team_strength_ratings_rejects_invalid_configuration(kwargs, message):
    with pytest.raises(ValueError, match=message):
        build_team_strength_ratings(_results(), **kwargs)


def test_team_strength_ratings_to_records_returns_sorted_extensible_records():
    ratings = {
        "B": TeamStrengthRating("B", 0.9, 1.1, 10),
        "A": TeamStrengthRating("A", 1.2, 0.8, 12),
    }

    records = team_strength_ratings_to_records(ratings)

    assert [record["team"] for record in records] == ["A", "B"]
    assert records[0] == {
        "team": "A",
        "attack_rating": 1.2,
        "defense_rating": 0.8,
        "matches_used": 12,
        "recent_form": {
            "form_5": None,
            "form_10": None,
            "form_20": None,
            "matches_available": 0,
        },
        "squad_strength": None,
    }


def test_export_team_metrics_writes_json(tmp_path):
    ratings = {
        "A": TeamStrengthRating("A", 1.2, 0.8, 12),
    }
    output_path = tmp_path / "metrics" / "team_metrics.json"

    recent_form_ratings = {
        "A": RecentFormRating("A", 1.1, 1.05, None, 12),
    }
    squad_strength_ratings = {
        "A": SquadStrengthRating("A", 210.0, 0.97),
    }

    exported = export_team_metrics(
        ratings,
        output_path,
        recent_form_ratings=recent_form_ratings,
        squad_strength_ratings=squad_strength_ratings,
    )
    loaded = json.loads(output_path.read_text(encoding="utf-8"))

    assert exported == loaded
    assert loaded == {
        "metrics_version": METRICS_VERSION,
        "squad_values_source": "data/external/teams_value.json",
        "squad_value_unit": "million_eur",
        "teams": [
            {
                "team": "A",
                "attack_rating": 1.2,
                "defense_rating": 0.8,
                "matches_used": 12,
                "recent_form": {
                    "form_5": 1.1,
                    "form_10": 1.05,
                    "form_20": None,
                    "matches_available": 12,
                },
                "squad_strength": {
                    "squad_value": 210.0,
                    "squad_strength_rating": 0.97,
                },
            }
        ]
    }
