"""Score the published World Cup 2026 forecast against the real results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.evaluation.match_probabilities import match_probabilities
from src.evaluation.world_cup_2026 import evaluate_forecast, read_actual_matches
from src.prediction.pipeline import load_prediction_inputs

PREDICTIONS_DIR = ROOT_DIR / "outputs" / "predictions"
ACTUAL_PATH = ROOT_DIR / "data" / "actual" / "world_cup_2026_results.csv"
OUTPUT_PATH = PREDICTIONS_DIR / "forecast_vs_actual.json"


def load(filename: str):
    return json.loads((PREDICTIONS_DIR / filename).read_text(encoding="utf-8"))


def main() -> None:
    actual = read_actual_matches(ACTUAL_PATH)
    inputs = load_prediction_inputs()
    knockout_probabilities = {
        match.match_number: match_probabilities(match.home_team, match.away_team, inputs)
        for match in actual
        if match.stage != "group"
    }
    report = evaluate_forecast(
        actual,
        load("tournament_predictions.json"),
        load("world_cup_probabilities.json"),
        load("group_results.json"),
        load("representative_tournament.json"),
        knockout_probabilities,
    )
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = report["summary"]
    group = report["group_stage"]["summary"]
    print(f"Saved {OUTPUT_PATH}")
    print(
        f"Champion {summary['champion']} (model rank {summary['champion_rank']}, "
        f"{summary['champion_probability']:.1%}); group outcomes {group['outcome_hits']}/{group['matches']}"
    )
    knockouts = report["knockout_summary"]
    print(f"Knockouts: model favourite advanced {knockouts['favourite_advanced']}/{knockouts['matches']}")


if __name__ == "__main__":
    main()
