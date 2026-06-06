from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.settings import (
    DEFAULT_CLI_SEED,
    DEFAULT_N_SIMULATIONS,
    DEFAULT_SQUAD_VALUES_PATH,
    DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH,
    DEFAULT_WORLD_CUP_2026_GROUPS_PATH,
    DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH,
    DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH,
)
from src.prediction.io.exports import (
    DEFAULT_GROUP_RESULTS_JSON_PATH,
    DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    DEFAULT_WORLD_CUP_TEAM_METRICS_JSON_PATH,
    DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
    export_group_results,
    export_match_predictions_json,
    export_probabilities,
    export_world_cup_team_metrics,
    validate_probability_output,
)
from src.prediction.tournament_flow.monte_carlo import run_monte_carlo
from src.prediction.tournament_flow.bracket_predictions import build_predicted_bracket_predictions
from src.prediction.pipeline import load_prediction_inputs, path_relative_to_project
from src.prediction.metrics.team_strength import export_team_metrics


def parse_args() -> argparse.Namespace:
    """Parse prediction pipeline CLI arguments."""

    parser = argparse.ArgumentParser(description="Run the V1 prediction pipeline end to end.")
    parser.add_argument(
        "--simulations",
        type=int,
        default=DEFAULT_N_SIMULATIONS,
        help="Number of simulations to run.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_CLI_SEED,
        help="Random seed for reproducible simulations.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
        help="JSON output path for aggregate probabilities.",
    )
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
        "--group-matches-config",
        type=Path,
        default=DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH,
        help="JSON file with ordered group-stage matches.",
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
    parser.add_argument(
        "--squad-values-config",
        type=Path,
        default=DEFAULT_SQUAD_VALUES_PATH,
        help="JSON file with squad market values.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the end-to-end prediction pipeline."""

    args = parse_args()

    print("Loading Elo rankings...")
    inputs = load_prediction_inputs(
        groups_config=args.groups_config,
        group_matches_config=args.group_matches_config,
        knockouts_config=args.knockouts_config,
        third_place_combinations_config=args.third_place_combinations_config,
        squad_values_config=args.squad_values_config,
    )
    team_metrics = export_team_metrics(
        inputs.team_strength_ratings,
        recent_form_ratings=inputs.recent_form_ratings,
        squad_strength_ratings=inputs.squad_strength_ratings,
        squad_values_source=path_relative_to_project(args.squad_values_config),
    )
    export_world_cup_team_metrics(team_metrics, inputs.groups)

    print(f"Running prediction pipeline with {args.simulations} simulations...")
    probabilities, outcomes = run_monte_carlo(
        groups=inputs.groups,
        ratings=inputs.ratings,
        knockout_matches=inputs.knockout_matches,
        third_place_combinations=inputs.third_place_combinations,
        simulations=args.simulations,
        seed=args.seed,
        return_outcomes=True,
        team_strength_ratings=inputs.team_strength_ratings,
        recent_form_ratings=inputs.recent_form_ratings,
        squad_strength_ratings=inputs.squad_strength_ratings,
        group_matches=inputs.group_matches,
    )

    df = export_probabilities(probabilities, args.output)
    validate_probability_output(df)
    export_group_results(outcomes, inputs.groups)

    match_predictions = build_predicted_bracket_predictions(
        outcomes=outcomes,
        groups=inputs.groups,
        ratings=inputs.ratings,
        knockout_matches=inputs.knockout_matches,
        third_place_combinations=inputs.third_place_combinations,
        team_strength_ratings=inputs.team_strength_ratings,
        recent_form_ratings=inputs.recent_form_ratings,
        group_matches=inputs.group_matches,
        squad_strength_ratings=inputs.squad_strength_ratings,
    )
    export_match_predictions_json(
        match_predictions,
        args.predictions_output,
        metadata={
            "simulations": args.simulations,
            "seed": args.seed,
            "method": "aggregate_group_stage_then_predicted_bracket",
            "team_strength_ratings": True,
            "recent_form": True,
            "squad_strength": True,
        },
    )

    print(f"Generated file: {args.output}")
    print(f"Generated predictions file: {args.predictions_output}")
    print(f"Generated World Cup team metrics file: {DEFAULT_WORLD_CUP_TEAM_METRICS_JSON_PATH}")
    print(f"Generated group results file: {DEFAULT_GROUP_RESULTS_JSON_PATH}")
    print(f"Simulations executed: {args.simulations}")
    print("Validation status: passed")
    print("\nTop 10 teams by champion probability:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
