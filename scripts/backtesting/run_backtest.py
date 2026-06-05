from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.elo import context as elo_context
from src.elo.export import get_latest_ratings
from src.elo.processor import process_matches
from src.prediction.io.exports import (
    export_match_predictions_json,
    export_probabilities,
    validate_probability_output,
)
from src.prediction.metrics.team_strength import export_team_metrics
from src.prediction.pipeline import load_prediction_inputs, path_relative_to_project
from src.prediction.settings import DEFAULT_CLI_SEED, DEFAULT_N_SIMULATIONS, PathSettings
from src.prediction.tournament_flow.bracket_predictions import (
    build_predicted_bracket_predictions,
)
from src.prediction.tournament_flow.monte_carlo import run_monte_carlo


RAW_RESULT_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
    "city",
    "country",
    "neutral",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the prediction pipeline against a backtesting dataset."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Dataset directory with raw, external, and processed subdirectories.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where backtest prediction outputs will be written.",
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=DEFAULT_N_SIMULATIONS,
        help="Number of Monte Carlo simulations to run.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_CLI_SEED,
        help="Random seed for reproducible simulations.",
    )
    parser.add_argument(
        "--skip-prepare",
        action="store_true",
        help="Reuse existing clean results and Elo files in processed/.",
    )
    return parser.parse_args()


def build_path_settings(dataset_dir: Path, output_dir: Path | None) -> PathSettings:
    output_dir = output_dir or Path("outputs/backtest") / dataset_dir.name
    return PathSettings(data_dir=dataset_dir, predictions_output_dir=output_dir)


def validate_required_inputs(paths: PathSettings) -> None:
    required_paths = [
        paths.raw_results_path,
        paths.former_names_path,
        paths.groups_path,
        paths.group_matches_path,
        paths.knockouts_path,
        paths.squad_values_path,
        paths.tournament_k_factors_path,
    ]
    missing = [path for path in required_paths if not Path(path).exists()]
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Missing required backtest input files:\n{formatted}")


def load_team_name_mapping(path: Path) -> dict[str, str]:
    former_names = pd.read_csv(path)
    if not {"former", "current"}.issubset(former_names.columns):
        raise ValueError("former_names.csv must contain 'former' and 'current' columns")

    return dict(zip(former_names["former"], former_names["current"], strict=True))


def build_clean_results(paths: PathSettings) -> pd.DataFrame:
    df = pd.read_csv(paths.raw_results_path)
    mapping = load_team_name_mapping(paths.former_names_path)

    df["date"] = pd.to_datetime(df["date"])
    df["home_team"] = df["home_team"].map(lambda team: mapping.get(team, team))
    df["away_team"] = df["away_team"].map(lambda team: mapping.get(team, team))
    df = df[RAW_RESULT_COLUMNS].copy()
    df = df.dropna(
        subset=[
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        ]
    )
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["neutral"] = df["neutral"].astype(bool)

    return df.sort_values("date").reset_index(drop=True)


def configure_tournament_k_factors(paths: PathSettings) -> None:
    elo_context.TOURNAMENT_K_FACTORS_PATH = paths.tournament_k_factors_path
    elo_context.load_tournament_k_factors.cache_clear()


def prepare_dataset(paths: PathSettings) -> None:
    paths.processed_data_dir.mkdir(parents=True, exist_ok=True)
    configure_tournament_k_factors(paths)

    clean_results = build_clean_results(paths)
    clean_results.to_csv(paths.clean_results_path, index=False)

    elo_history = process_matches(clean_results)
    elo_history.to_csv(paths.elo_history_path, index=False)

    rankings = get_latest_ratings(elo_history)
    rankings.to_csv(paths.elo_rankings_path, index=False)


def run_backtest(paths: PathSettings, simulations: int, seed: int) -> pd.DataFrame:
    configure_tournament_k_factors(paths)
    inputs = load_prediction_inputs(
        path_settings=paths,
        allow_missing_third_place_combinations=True,
    )
    third_place_combinations = (
        inputs.third_place_combinations
        if Path(paths.third_place_combinations_path).exists()
        else None
    )

    export_team_metrics(
        inputs.team_strength_ratings,
        output_path=paths.team_metrics_path,
        recent_form_ratings=inputs.recent_form_ratings,
        squad_strength_ratings=inputs.squad_strength_ratings,
        squad_values_source=path_relative_to_project(paths.squad_values_path),
    )

    probabilities, outcomes = run_monte_carlo(
        groups=inputs.groups,
        ratings=inputs.ratings,
        knockout_matches=inputs.knockout_matches,
        third_place_combinations=third_place_combinations,
        simulations=simulations,
        seed=seed,
        return_outcomes=True,
        team_strength_ratings=inputs.team_strength_ratings,
        recent_form_ratings=inputs.recent_form_ratings,
        squad_strength_ratings=inputs.squad_strength_ratings,
        group_matches=inputs.group_matches,
    )

    df = export_probabilities(probabilities, paths.world_cup_probabilities_path)
    validate_probability_output(df)

    match_predictions = build_predicted_bracket_predictions(
        outcomes=outcomes,
        groups=inputs.groups,
        ratings=inputs.ratings,
        knockout_matches=inputs.knockout_matches,
        third_place_combinations=third_place_combinations,
        team_strength_ratings=inputs.team_strength_ratings,
        recent_form_ratings=inputs.recent_form_ratings,
        group_matches=inputs.group_matches,
        squad_strength_ratings=inputs.squad_strength_ratings,
    )
    export_match_predictions_json(
        match_predictions,
        paths.tournament_predictions_path,
        metadata={
            "dataset": str(paths.data_dir),
            "simulations": simulations,
            "seed": seed,
            "method": "backtest_aggregate_group_stage_then_predicted_bracket",
            "team_strength_ratings": True,
            "recent_form": True,
            "squad_strength": True,
        },
    )

    return df


def main() -> None:
    args = parse_args()
    paths = build_path_settings(args.dataset, args.output_dir)

    validate_required_inputs(paths)
    if not args.skip_prepare:
        prepare_dataset(paths)

    df = run_backtest(paths, args.simulations, args.seed)

    print(f"Dataset: {paths.data_dir}")
    print(f"Clean results: {paths.clean_results_path}")
    print(f"Elo history: {paths.elo_history_path}")
    print(f"Elo rankings: {paths.elo_rankings_path}")
    print(f"Team metrics: {paths.team_metrics_path}")
    print(f"Probabilities: {paths.world_cup_probabilities_path}")
    print(f"Predictions: {paths.tournament_predictions_path}")
    print(f"Simulations executed: {args.simulations}")
    print("Validation status: passed")
    print("\nTop 10 teams by champion probability:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
