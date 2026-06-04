from unittest.mock import patch

import pandas as pd
import pytest

from src.prediction.ratings import load_ratings


def test_load_ratings_returns_team_to_elo_mapping():
    rankings = pd.DataFrame(
        {
            "rank": [1, 2],
            "team": ["Spain", "France"],
            "elo": [1984.02, 1948.33],
        }
    )

    with patch("src.prediction.ratings.pd.read_csv", return_value=rankings):
        ratings = load_ratings()

    assert ratings == {"Spain": 1984.02, "France": 1948.33}


def test_load_ratings_rejects_missing_required_columns():
    rankings = pd.DataFrame({"team": ["Spain"]})

    with patch("src.prediction.ratings.pd.read_csv", return_value=rankings):
        with pytest.raises(ValueError, match="elo"):
            load_ratings()
