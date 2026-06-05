import pandas as pd
import pytest

from src.data.validation import (
    validate_clean_results_dataframe,
    validate_world_cup_external_configs,
)
from src.prediction.config import (
    DEFAULT_SQUAD_VALUES_PATH,
    DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH,
    DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
    DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
    DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
)
from src.prediction.ratings import DEFAULT_ELO_RANKINGS_PATH


def valid_clean_results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "home_team": ["Team A"],
            "away_team": ["Team B"],
            "home_score": [1],
            "away_score": [0],
            "tournament": ["Friendly"],
            "neutral": [False],
        }
    )


def test_validate_clean_results_accepts_valid_dataframe():
    validate_clean_results_dataframe(valid_clean_results())


def test_validate_clean_results_rejects_same_home_and_away_team():
    df = valid_clean_results()
    df.loc[0, "away_team"] = "Team A"

    with pytest.raises(ValueError, match="same home and away team"):
        validate_clean_results_dataframe(df)


def test_default_world_cup_external_configs_are_consistent():
    validate_world_cup_external_configs(
        groups_path=DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
        group_matches_path=DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH,
        knockouts_path=DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
        third_place_combinations_path=DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
        squad_values_path=DEFAULT_SQUAD_VALUES_PATH,
        elo_rankings_path=DEFAULT_ELO_RANKINGS_PATH,
    )
