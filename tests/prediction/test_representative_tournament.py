from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from src.prediction.config import load_knockouts_config
from src.prediction.core.models import MatchPrediction
from src.prediction.settings import (
    DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
)
from src.prediction.tournament_flow.representative_tournament import (
    build_representative_tournament,
    validate_representative_tournament,
)


def current_representative_tournament() -> tuple[dict, list[dict[str, str]]]:
    with Path(DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH).open(encoding="utf-8") as file:
        predictions = [
            MatchPrediction(**record)
            for record in json.load(file)["matches"]
        ]
    knockouts = load_knockouts_config(DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH)
    return build_representative_tournament(predictions, knockouts), knockouts


def test_representative_tournament_is_coherent_end_to_end():
    representative, knockouts = current_representative_tournament()

    validate_representative_tournament(representative, knockouts)

    assert len(representative["groups"]) == 12
    assert len(representative["qualified"]["round_of_32"]) == 32
    assert len(representative["bracket"]) == 32
    assert representative["champion"] is not None


def test_representative_validation_rejects_standing_inconsistent_with_results():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    inconsistent["groups"]["A"][0]["points"] += 1

    with pytest.raises(ValueError, match="standings field points"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_qualifiers_inconsistent_with_standings():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    inconsistent["qualified"]["round_of_32"][0] = "Not a qualifier"

    with pytest.raises(ValueError, match="qualifiers"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_bracket_inconsistent_with_qualifiers():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    first_round = next(match for match in inconsistent["bracket"] if match["round"] == "round_of_32")
    first_round["home_team"] = "Not a qualifier"

    with pytest.raises(ValueError, match="bracket"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_team_without_previous_round_win():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    round_of_16 = next(match for match in inconsistent["bracket"] if match["round"] == "round_of_16")
    round_of_16["home_team"] = "Not a previous winner"

    with pytest.raises(ValueError, match="winner path is inconsistent"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_duplicate_team_in_round():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    round_matches = [
        match for match in inconsistent["bracket"] if match["round"] == "quarter_final"
    ]
    round_matches[1]["home_team"] = round_matches[0]["home_team"]
    round_matches[1]["winner"] = round_matches[0]["home_team"]
    round_matches[1]["predicted_winner"] = round_matches[0]["home_team"]

    with pytest.raises(ValueError, match="appears twice"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_empty_team():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    inconsistent["bracket"][0]["home_team"] = ""

    with pytest.raises(ValueError, match="empty team"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_champion_inconsistent_with_final():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    inconsistent["champion"] = "Not the final winner"

    with pytest.raises(ValueError, match="champion"):
        validate_representative_tournament(inconsistent, knockouts)


def test_representative_validation_rejects_score_contradicting_displayed_outcome():
    representative, knockouts = current_representative_tournament()
    inconsistent = copy.deepcopy(representative)
    group_match = next(
        match for match in inconsistent["results"] if match["stage"] == "group"
    )
    group_match["predicted_winner"] = group_match["home_team"]
    group_match["predicted_home_goals"] = 0
    group_match["predicted_away_goals"] = 1

    with pytest.raises(ValueError, match="score contradicts displayed outcome"):
        validate_representative_tournament(inconsistent, knockouts)
