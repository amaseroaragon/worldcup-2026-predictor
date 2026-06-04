import json
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.prediction.config import (
    DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH,
    DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
    DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
    DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
    load_groups_config,
    load_group_matches_config,
    load_knockouts_config,
    load_third_place_combinations_config,
)


CONFIG_PATH = Path("config.json")


@contextmanager
def mocked_config(data):
    with patch("pathlib.Path.exists", return_value=True), patch(
        "pathlib.Path.open",
        mock_open(read_data=json.dumps(data)),
    ):
        yield CONFIG_PATH


def test_load_groups_config_returns_groups_from_json():
    with mocked_config(
        {
            "groups": {
                "A": ["Mexico", "South Africa", "Team A3", "Team A4"],
                "B": ["Canada", "Team B2", "Team B3", "Team B4"],
            }
        }
    ) as path:
        groups = load_groups_config(path)

    assert groups == {
        "A": ["Mexico", "South Africa", "Team A3", "Team A4"],
        "B": ["Canada", "Team B2", "Team B3", "Team B4"],
    }


def test_load_groups_config_rejects_missing_file():
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="does not exist"):
            load_groups_config("missing.json")


def test_load_groups_config_rejects_missing_groups_key():
    with mocked_config({"teams": {}}) as path:
        with pytest.raises(ValueError, match="'groups' key"):
            load_groups_config(path)


def test_load_groups_config_rejects_group_without_four_teams():
    with mocked_config({"groups": {"A": ["Mexico", "Canada", "Japan"]}}) as path:
        with pytest.raises(ValueError, match="exactly 4 teams"):
            load_groups_config(path)


def test_load_groups_config_rejects_non_string_team_names():
    with mocked_config({"groups": {"A": ["Mexico", "Canada", "Japan", 123]}}) as path:
        with pytest.raises(ValueError, match="string team names"):
            load_groups_config(path)


def test_default_world_cup_2026_groups_config_is_loadable():
    groups = load_groups_config(DEFAULT_WORLD_CUP_2026_GROUPS_PATH)

    assert set(groups) == set("ABCDEFGHIJKL")


def test_load_group_matches_config_generates_ids_and_orders_by_matchday_then_id():
    with mocked_config(
        {
            "matches": [
                {"match_id": "group_A_2", "group": "A", "matchday": 2, "home": "A", "away": "B"},
                {"match_id": "group_A_3", "group": "A", "matchday": 1, "home": "C", "away": "D"},
                {"match_id": "group_A_1", "group": "A", "matchday": 1, "home": "A", "away": "C"},
                {"group": "B", "home": "E", "away": "F"},
            ]
        }
    ) as path:
        matches = load_group_matches_config(path)

    assert [match["match_id"] for match in matches] == [
        "group_B_1",
        "group_A_1",
        "group_A_3",
        "group_A_2",
    ]


def test_default_world_cup_2026_group_matches_config_is_loadable():
    matches = load_group_matches_config(DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH)

    assert len(matches) == 72
    assert [match["matchday"] for match in matches] == sorted(
        match["matchday"] for match in matches
    )


def test_load_knockouts_config_returns_matches_from_json():
    with mocked_config(
        {
            "matches": [
                {
                    "match_id": "M73",
                    "round": "round_of_32",
                    "home": "2A",
                    "away": "2B",
                }
            ]
        }
    ) as path:
        matches = load_knockouts_config(path)

    assert matches == [
        {
            "match_id": "M73",
            "round": "round_of_32",
            "home": "2A",
            "away": "2B",
        }
    ]


def test_load_knockouts_config_rejects_missing_matches_key():
    with mocked_config({"rounds": []}) as path:
        with pytest.raises(ValueError, match="'matches' key"):
            load_knockouts_config(path)


def test_load_knockouts_config_rejects_missing_match_fields():
    with mocked_config({"matches": [{"match_id": "M73"}]}) as path:
        with pytest.raises(ValueError, match="missing required fields"):
            load_knockouts_config(path)


def test_default_world_cup_2026_knockouts_config_is_loadable():
    matches = load_knockouts_config(DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH)

    assert len(matches) == 32
    assert matches[0]["match_id"] == "M73"
    assert matches[-1]["match_id"] == "M104"


def test_load_third_place_combinations_config_returns_placeholder_resolutions():
    with mocked_config(
        {
            "by_best_thirds": {
                "ABCDEFGH": {
                    "placeholder_resolution": {
                        "3ABCDF": "3A",
                        "3CDFGH": "3H",
                    }
                }
            }
        }
    ) as path:
        combinations = load_third_place_combinations_config(path)

    assert combinations == {
        "ABCDEFGH": {
            "3ABCDF": "3A",
            "3CDFGH": "3H",
        }
    }


def test_load_third_place_combinations_config_rejects_missing_by_best_thirds():
    with mocked_config({"combinations": {}}) as path:
        with pytest.raises(ValueError, match="'by_best_thirds' key"):
            load_third_place_combinations_config(path)


def test_default_world_cup_2026_third_place_combinations_config_is_loadable():
    combinations = load_third_place_combinations_config(
        DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH
    )

    assert len(combinations) == 495
