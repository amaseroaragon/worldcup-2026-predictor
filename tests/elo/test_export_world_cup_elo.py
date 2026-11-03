import pytest

from scripts.elo.export_world_cup_elo import build_world_cup_elo


def test_build_world_cup_elo_ranks_field_and_world():
    rankings = [
        {"team": "A", "elo": "1900", "date": "2026-06-01"},
        {"team": "X", "elo": "2000", "date": "2026-06-01"},
        {"team": "B", "elo": "1800", "date": "2026-06-01"},
    ]

    result = build_world_cup_elo(rankings, {"A": ["A", "B"]})

    assert [(r["team"], r["world_rank"], r["field_rank"]) for r in result] == [("A", 2, 1), ("B", 3, 2)]


def test_build_world_cup_elo_requires_every_team():
    with pytest.raises(ValueError, match="Missing Elo ratings"):
        build_world_cup_elo([{"team": "A", "elo": "1900", "date": "2026-06-01"}], {"A": ["A", "B"]})
