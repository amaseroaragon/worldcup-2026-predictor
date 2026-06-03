from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.export import export_probabilities, validate_probability_output
from src.prediction.monte_carlo import run_monte_carlo
from src.prediction.ratings import load_ratings


OUTPUT_PATH = Path("data/processed/world_cup_probabilities.csv")

GROUPS_V1 = {
    "A": ["Argentina", "Mexico", "Senegal", "Japan"],
    "B": ["Spain", "United States", "Morocco", "South Korea"],
    "C": ["France", "Canada", "Iran", "Ecuador"],
    "D": ["Brazil", "England", "Portugal", "Netherlands"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the V1 prediction pipeline end to end.")
    parser.add_argument("--simulations", type=int, default=1000, help="Number of simulations to run.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible simulations.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="CSV output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("Loading Elo rankings...")
    ratings = load_ratings()

    print(f"Running prediction pipeline with {args.simulations} simulations...")
    probabilities = run_monte_carlo(
        groups=GROUPS_V1,
        ratings=ratings,
        simulations=args.simulations,
        seed=args.seed,
    )

    df = export_probabilities(probabilities, args.output)
    validate_probability_output(df)

    print(f"Generated file: {args.output}")
    print(f"Simulations executed: {args.simulations}")
    print("Validation status: passed")
    print("\nTop 10 teams by champion probability:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
