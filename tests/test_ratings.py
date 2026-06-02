import pandas as pd
import pytest

from src.prediction.ratings import load_ratings


def test_load_ratings_returns_team_to_elo_mapping(tmp_path):
    path = tmp_path / "elo_rankings.csv"
    pd.DataFrame(
        {
            "rank": [1, 2],
            "team": ["Spain", "France"],
            "elo": [1984.02, 1948.33],
        }
    ).to_csv(path, index=False)

    ratings = load_ratings(path)

    assert ratings == {"Spain": 1984.02, "France": 1948.33}


def test_load_ratings_rejects_missing_required_columns(tmp_path):
    path = tmp_path / "elo_rankings.csv"
    pd.DataFrame({"team": ["Spain"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="elo"):
        load_ratings(path)
