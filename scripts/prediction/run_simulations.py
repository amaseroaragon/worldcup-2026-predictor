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
from src.prediction.export import export_probabilities
from src.prediction.monte_carlo import run_monte_carlo
from src.prediction.ratings import load_ratings


OUTPUT_PATH = Path("data/processed/world_cup_probabilities.csv")


def parse_args() -> argparse.Namespace:
    """Parse Monte Carlo simulation CLI arguments."""

    parser = argparse.ArgumentParser(description="Run V1 World Cup Monte Carlo simulations.")
    parser.add_argument("--simulations", type=int, default=1000, help="Number of tournament simulations to run.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible simulations.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="CSV output path.")
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
    """Run Monte Carlo simulations and export aggregate probabilities."""

    args = parse_args()

    print("Loading Elo rankings...")
    ratings = load_ratings()
    groups = load_groups_config(args.groups_config)
    knockout_matches = load_knockouts_config(args.knockouts_config)
    third_place_combinations = load_third_place_combinations_config(args.third_place_combinations_config)

    print(f"Running {args.simulations} simulations...")
    probabilities = run_monte_carlo(
        groups=groups,
        ratings=ratings,
        knockout_matches=knockout_matches,
        third_place_combinations=third_place_combinations,
        simulations=args.simulations,
        seed=args.seed,
    )

    df = export_probabilities(probabilities, args.output)

    print(f"Probabilities exported to: {args.output}")
    print(f"Simulations executed: {args.simulations}")
    print("\nTop 10 favorites:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
