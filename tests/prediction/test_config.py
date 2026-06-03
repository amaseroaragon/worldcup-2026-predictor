import json

import pytest

from src.prediction.config import (
    DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
    DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
    DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
    load_groups_config,
    load_knockouts_config,
    load_third_place_combinations_config,
)


def write_groups_config(tmp_path, data):
    path = tmp_path / "groups.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_knockouts_config(tmp_path, data):
    path = tmp_path / "knockouts.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_third_place_combinations_config(tmp_path, data):
    path = tmp_path / "third_place_combinations.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_groups_config_returns_groups_from_json(tmp_path):
    path = write_groups_config(
        tmp_path,
        {
            "groups": {
                "A": ["Mexico", "South Africa", "Team A3", "Team A4"],
                "B": ["Canada", "Team B2", "Team B3", "Team B4"],
            }
        },
    )

    groups = load_groups_config(path)

    assert groups == {
        "A": ["Mexico", "South Africa", "Team A3", "Team A4"],
        "B": ["Canada", "Team B2", "Team B3", "Team B4"],
    }


def test_load_groups_config_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_groups_config(tmp_path / "missing.json")


def test_load_groups_config_rejects_missing_groups_key(tmp_path):
    path = write_groups_config(tmp_path, {"teams": {}})

    with pytest.raises(ValueError, match="'groups' key"):
        load_groups_config(path)


def test_load_groups_config_rejects_group_without_four_teams(tmp_path):
    path = write_groups_config(tmp_path, {"groups": {"A": ["Mexico", "Canada", "Japan"]}})

    with pytest.raises(ValueError, match="exactly 4 teams"):
        load_groups_config(path)


def test_load_groups_config_rejects_non_string_team_names(tmp_path):
    path = write_groups_config(tmp_path, {"groups": {"A": ["Mexico", "Canada", "Japan", 123]}})

    with pytest.raises(ValueError, match="string team names"):
        load_groups_config(path)


def test_default_world_cup_2026_groups_config_is_loadable():
    groups = load_groups_config(DEFAULT_WORLD_CUP_2026_GROUPS_PATH)

    assert set(groups) == set("ABCDEFGHIJKL")


def test_load_knockouts_config_returns_matches_from_json(tmp_path):
    path = write_knockouts_config(
        tmp_path,
        {
            "matches": [
                {
                    "match_id": "M73",
                    "round": "round_of_32",
                    "home": "2A",
                    "away": "2B",
                }
            ]
        },
    )

    matches = load_knockouts_config(path)

    assert matches == [
        {
            "match_id": "M73",
            "round": "round_of_32",
            "home": "2A",
            "away": "2B",
        }
    ]


def test_load_knockouts_config_rejects_missing_matches_key(tmp_path):
    path = write_knockouts_config(tmp_path, {"rounds": []})

    with pytest.raises(ValueError, match="'matches' key"):
        load_knockouts_config(path)


def test_load_knockouts_config_rejects_missing_match_fields(tmp_path):
    path = write_knockouts_config(tmp_path, {"matches": [{"match_id": "M73"}]})

    with pytest.raises(ValueError, match="missing required fields"):
        load_knockouts_config(path)


def test_default_world_cup_2026_knockouts_config_is_loadable():
    matches = load_knockouts_config(DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH)

    assert len(matches) == 32
    assert matches[0]["match_id"] == "M73"
    assert matches[-1]["match_id"] == "M104"


def test_load_third_place_combinations_config_returns_placeholder_resolutions(tmp_path):
    path = write_third_place_combinations_config(
        tmp_path,
        {
            "by_best_thirds": {
                "ABCDEFGH": {
                    "placeholder_resolution": {
                        "3ABCDF": "3A",
                        "3CDFGH": "3H",
                    }
                }
            }
        },
    )

    combinations = load_third_place_combinations_config(path)

    assert combinations == {
        "ABCDEFGH": {
            "3ABCDF": "3A",
            "3CDFGH": "3H",
        }
    }


def test_load_third_place_combinations_config_rejects_missing_by_best_thirds(tmp_path):
    path = write_third_place_combinations_config(tmp_path, {"combinations": {}})

    with pytest.raises(ValueError, match="'by_best_thirds' key"):
        load_third_place_combinations_config(path)


def test_default_world_cup_2026_third_place_combinations_config_is_loadable():
    combinations = load_third_place_combinations_config(
        DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH
    )

    assert len(combinations) == 495
