from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.config import (
    DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
    DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
    DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
    load_groups_config,
    load_knockouts_config,
    load_third_place_combinations_config,
)
from src.prediction.export import (
    DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    build_predicted_bracket_predictions,
    export_match_predictions_json,
    export_probabilities,
    validate_probability_output,
)
from src.prediction.monte_carlo import run_monte_carlo
from src.prediction.ratings import load_ratings


OUTPUT_PATH = Path("data/processed/world_cup_probabilities.csv")


def parse_args() -> argparse.Namespace:
    """Parse prediction pipeline CLI arguments."""

    parser = argparse.ArgumentParser(description="Run the V1 prediction pipeline end to end.")
    parser.add_argument("--simulations", type=int, default=1000, help="Number of simulations to run.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible simulations.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="CSV output path.")
    parser.add_argument(
        "--predictions-output",
        type=Path,
        default=DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
        help="JSON output path for match predictions.",
    )
    parser.add_argument(
        "--groups-config",
        type=Path,
        default=DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
        help="JSON file with tournament groups.",
    )
    parser.add_argument(
        "--knockouts-config",
        type=Path,
        default=DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
        help="JSON file with tournament knockout bracket.",
    )
    parser.add_argument(
        "--third-place-combinations-config",
        type=Path,
        default=DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
        help="JSON file with official third-place matchup combinations.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the end-to-end prediction pipeline."""

    args = parse_args()

    print("Loading Elo rankings...")
    ratings = load_ratings()
    groups = load_groups_config(args.groups_config)
    knockout_matches = load_knockouts_config(args.knockouts_config)
    third_place_combinations = load_third_place_combinations_config(args.third_place_combinations_config)

    print(f"Running prediction pipeline with {args.simulations} simulations...")
    probabilities, outcomes = run_monte_carlo(
        groups=groups,
        ratings=ratings,
        knockout_matches=knockout_matches,
        third_place_combinations=third_place_combinations,
        simulations=args.simulations,
        seed=args.seed,
        return_outcomes=True,
    )

    df = export_probabilities(probabilities, args.output)
    validate_probability_output(df)

    match_predictions = build_predicted_bracket_predictions(
        outcomes,
        groups,
        ratings,
        knockout_matches,
        third_place_combinations,
    )
    export_match_predictions_json(
        match_predictions,
        args.predictions_output,
        metadata={
            "simulations": args.simulations,
            "seed": args.seed,
            "method": "aggregate_group_stage_then_predicted_bracket",
        },
    )

    print(f"Generated file: {args.output}")
    print(f"Generated predictions file: {args.predictions_output}")
    print(f"Simulations executed: {args.simulations}")
    print("Validation status: passed")
    print("\nTop 10 teams by champion probability:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
