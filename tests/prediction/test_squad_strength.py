import json
from dataclasses import FrozenInstanceError

import pytest

from src.prediction.metrics.squad_strength import (
    SquadStrengthRating,
    build_squad_strength_ratings,
    load_squad_values,
)


def test_load_squad_values_reads_team_values(tmp_path):
    path = tmp_path / "squad_values.json"
    path.write_text(
        json.dumps({"teams": {"Spain": 1362.5, "France": 1650.0}}),
        encoding="utf-8",
    )

    values = load_squad_values(path)

    assert values == {"Spain": 1362.5, "France": 1650.0}


def test_load_squad_values_rejects_invalid_shape(tmp_path):
    path = tmp_path / "squad_values.json"
    path.write_text(json.dumps({"countries": {}}), encoding="utf-8")

    with pytest.raises(ValueError, match="teams"):
        load_squad_values(path)


@pytest.mark.parametrize(
    "payload",
    [
        {"teams": {"Spain": "expensive"}},
        {"teams": {"Spain": -1.0}},
    ],
)
def test_load_squad_values_rejects_invalid_values(tmp_path, payload):
    path = tmp_path / "squad_values.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError):
        load_squad_values(path)


def test_build_squad_strength_ratings_normalizes_log_values():
    ratings = build_squad_strength_ratings(
        {
            "Low": 49.5,
            "High": 1650.0,
        },
        min_rating=0.01,
        max_rating=10.0,
    )

    assert ratings["Low"].squad_strength_rating < 1.0
    assert ratings["High"].squad_strength_rating > 1.0
    assert ratings["High"].squad_value == 1650.0


def test_build_squad_strength_ratings_clips_extreme_ratings():
    ratings = build_squad_strength_ratings(
        {
            "Low": 1.0,
            "High": 10000.0,
        },
        min_rating=0.85,
        max_rating=1.15,
    )

    assert ratings["Low"].squad_strength_rating == 0.85
    assert ratings["High"].squad_strength_rating == 1.15


def test_build_squad_strength_ratings_returns_empty_mapping_for_empty_values():
    assert build_squad_strength_ratings({}) == {}


def test_build_squad_strength_ratings_uses_neutral_rating_when_all_values_are_zero():
    ratings = build_squad_strength_ratings({"A": 0.0, "B": 0.0})

    assert ratings["A"].squad_strength_rating == 1.0
    assert ratings["B"].squad_strength_rating == 1.0


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"min_rating": 0.0}, "rating bounds"),
        ({"min_rating": 1.2, "max_rating": 1.0}, "min_rating"),
    ],
)
def test_build_squad_strength_ratings_rejects_invalid_configuration(kwargs, message):
    with pytest.raises(ValueError, match=message):
        build_squad_strength_ratings({"Spain": 1362.5}, **kwargs)


def test_build_squad_strength_ratings_rejects_negative_values():
    with pytest.raises(ValueError, match="non-negative"):
        build_squad_strength_ratings({"Spain": -1.0})


def test_squad_strength_rating_is_frozen():
    rating = SquadStrengthRating("Spain", 1362.5, 1.15)

    with pytest.raises(FrozenInstanceError):
        rating.squad_strength_rating = 1.0  # type: ignore[misc]
