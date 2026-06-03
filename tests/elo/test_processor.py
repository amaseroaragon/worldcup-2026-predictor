import pandas as pd
import pytest

from src.elo.processor import process_matches


def test_process_matches_keeps_legacy_behavior_without_context_columns():
    matches = pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "home_team": "A",
                "away_team": "B",
                "home_score": 1,
                "away_score": 0,
                "neutral": True,
            }
        ]
    )

    history = process_matches(matches)

    assert history.loc[0, "home_elo_after"] == 1510.0
    assert history.loc[0, "away_elo_after"] == 1490.0


def test_process_matches_uses_context_columns_when_present():
    matches = pd.DataFrame(
        [
            {
                "date": "2026-01-01",
                "home_team": "A",
                "away_team": "B",
                "home_score": 4,
                "away_score": 0,
                "neutral": True,
                "tournament": "FIFA World Cup",
            }
        ]
    )

    history = process_matches(matches)

    assert history.loc[0, "home_elo_after"] == pytest.approx(1540.24)
    assert history.loc[0, "away_elo_after"] == pytest.approx(1459.76)
