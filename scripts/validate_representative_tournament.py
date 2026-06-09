from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.config import load_knockouts_config
from src.prediction.settings import DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH
from src.prediction.tournament_flow.representative_tournament import (
    validate_representative_tournament,
)


DEFAULT_INPUT = ROOT_DIR / "outputs" / "predictions" / "representative_tournament.json"
ROUND_ORDER = (
    "round_of_32",
    "round_of_16",
    "quarter_final",
    "semi_final",
    "third_place_playoff",
    "final",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and trace the coherent representative tournament."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--knockouts-config",
        type=Path,
        default=DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.input.open(encoding="utf-8") as file:
        representative = json.load(file)["representative_tournament"]
    knockouts = load_knockouts_config(args.knockouts_config)

    validate_representative_tournament(representative, knockouts)

    print("Group qualifiers:")
    for group, standings in representative["groups"].items():
        print(f"{group}1 {standings[0]['team']}")
        print(f"{group}2 {standings[1]['team']}")

    print("\nBest third-place qualifiers:")
    for row in representative["best_third_places"]:
        if row["qualified"]:
            print(f"{row['rank']}. Group {row['group']} - {row['team']}")

    for round_name in ROUND_ORDER:
        matches = [
            match for match in representative["bracket"]
            if match["round"] == round_name
        ]
        if not matches:
            continue
        print(f"\n{round_name.replace('_', ' ').title()}:")
        for match in matches:
            print(
                f"{match['match_id']}: {match['home_team']} vs {match['away_team']} "
                f"-> {match['winner']} "
                f"({match['source']['home']} / {match['source']['away']})"
            )

    print(f"\nChampion: {representative['champion']}")
    print("\nRepresentative tournament validation passed")


if __name__ == "__main__":
    main()
