from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Iterator

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from scripts.backtesting.run_backtest import (  # noqa: E402
    build_path_settings,
    configure_tournament_k_factors,
    prepare_dataset,
    validate_required_inputs,
)
from src.backtesting.metrics import (  # noqa: E402
    brier_binary_event,
    brier_champion,
    champion_rank,
    real_champion_probability,
    top_k_hit,
)
from src.backtesting.model_variants import MODEL_VARIANTS, ModelVariant  # noqa: E402
from src.prediction import config as prediction_config  # noqa: E402
from src.prediction.io.exports import probabilities_to_dataframe  # noqa: E402
from src.prediction.metrics.team_strength import TeamStrengthRating  # noqa: E402
from src.prediction.pipeline import load_prediction_inputs  # noqa: E402
from src.prediction.settings import DEFAULT_CLI_SEED, DEFAULT_N_SIMULATIONS, PathSettings  # noqa: E402
from src.prediction.tournament_flow.monte_carlo import run_monte_carlo  # noqa: E402


DEFAULT_RESULTS_PATH = Path("data/backtest/model_variant_comparison.csv")

BACKTEST_TOURNAMENTS = {
    "world_cup_2018": Path("data/backtest/world-cup-2018"),
    "world_cup_2022": Path("data/backtest/world-cup-2022"),
    "euro_2024": Path("data/backtest/euro-cup-2024"),
}

TOURNAMENT_TRUTHS = {
    "world_cup_2018": {
        "champion": "France",
        "finalists": {"France", "Croatia"},
        "semifinalists": {"France", "Belgium", "Croatia", "England"},
        "quarterfinalists": {
            "Uruguay",
            "France",
            "Brazil",
            "Belgium",
            "Russia",
            "Croatia",
            "Sweden",
            "England",
        },
    },
    "world_cup_2022": {
        "champion": "Argentina",
        "finalists": {"Argentina", "France"},
        "semifinalists": {"Argentina", "Croatia", "France", "Morocco"},
        "quarterfinalists": {
            "Argentina",
            "Netherlands",
            "France",
            "England",
            "Morocco",
            "Portugal",
            "Croatia",
            "Brazil",
        },
    },
    "euro_2024": {
        "champion": "Spain",
        "finalists": {"Spain", "England"},
        "semifinalists": {"Spain", "France", "Netherlands", "England"},
        "quarterfinalists": {
            "Spain",
            "Germany",
            "Portugal",
            "France",
            "England",
            "Switzerland",
            "Netherlands",
            "Turkey",
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate backtesting model variants across historical tournaments."
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=DEFAULT_N_SIMULATIONS,
        help="Number of Monte Carlo simulations per variant and tournament.",
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
        default=DEFAULT_RESULTS_PATH,
        help="CSV path for the model variant comparison.",
    )
    parser.add_argument(
        "--skip-prepare",
        action="store_true",
        help="Reuse existing clean results and Elo files in each backtest dataset.",
    )
    return parser.parse_args()


def evaluate_all_variants(
    *,
    simulations: int,
    seed: int,
    skip_prepare: bool,
) -> pd.DataFrame:
    """Evaluate every configured variant against every backtest tournament."""

    rows = []
    for tournament, dataset_dir in BACKTEST_TOURNAMENTS.items():
        paths = build_path_settings(dataset_dir, output_dir=None)
        validate_required_inputs(paths)
        if not skip_prepare:
            prepare_dataset(paths)

        for variant in MODEL_VARIANTS:
            rows.append(
                evaluate_variant_for_tournament(
                    tournament=tournament,
                    paths=paths,
                    variant=variant,
                    simulations=simulations,
                    seed=seed,
                )
            )

    return pd.DataFrame(rows)


def evaluate_variant_for_tournament(
    *,
    tournament: str,
    paths: PathSettings,
    variant: ModelVariant,
    simulations: int,
    seed: int,
) -> dict[str, object]:
    """Evaluate one model variant against one backtest tournament."""

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

    team_strength_ratings = apply_team_strength_variant(
        inputs.team_strength_ratings,
        variant,
    )
    recent_form_ratings = inputs.recent_form_ratings if variant.use_recent_form else None
    squad_strength_ratings = (
        inputs.squad_strength_ratings if variant.use_squad_strength else None
    )

    with patched_dynamic_elo_flags(variant):
        probabilities, outcomes = run_monte_carlo(
            groups=inputs.groups,
            ratings=inputs.ratings,
            knockout_matches=inputs.knockout_matches,
            third_place_combinations=third_place_combinations,
            simulations=simulations,
            seed=seed,
            return_outcomes=True,
            team_strength_ratings=team_strength_ratings,
            recent_form_ratings=recent_form_ratings,
            squad_strength_ratings=squad_strength_ratings,
            group_matches=inputs.group_matches,
        )

    probability_rows = build_evaluation_probability_rows(probabilities, outcomes, inputs.groups)
    truth = TOURNAMENT_TRUTHS[tournament]
    real_champion = str(truth["champion"])
    predicted_champion = str(probability_rows[0]["team"])

    return {
        "tournament": tournament,
        "variant": variant.name,
        "n_simulations": simulations,
        "seed": seed,
        "real_champion": real_champion,
        "predicted_champion": predicted_champion,
        "champion_probability": probability_rows[0]["champion_probability"],
        "real_champion_probability": real_champion_probability(
            probability_rows,
            real_champion,
        ),
        "real_champion_rank": champion_rank(probability_rows, real_champion),
        "top_3_hit": top_k_hit(probability_rows, real_champion, 3),
        "top_5_hit": top_k_hit(probability_rows, real_champion, 5),
        "brier_champion": brier_champion(probability_rows, real_champion),
        "brier_final": brier_binary_event(
            probability_rows,
            actual_positive_teams=set(truth["finalists"]),
            probability_column="final_probability",
        ),
        "brier_semifinal": brier_binary_event(
            probability_rows,
            actual_positive_teams=set(truth["semifinalists"]),
            probability_column="semifinal_probability",
        ),
        "brier_quarterfinal": brier_binary_event(
            probability_rows,
            actual_positive_teams=set(truth["quarterfinalists"]),
            probability_column="quarterfinal_probability",
        ),
        "stage_accuracy": None,
    }


def apply_team_strength_variant(
    ratings: dict[str, TeamStrengthRating],
    variant: ModelVariant,
) -> dict[str, TeamStrengthRating] | None:
    """Apply attack/defense switches without mutating source ratings."""

    if not variant.use_attack_rating and not variant.use_defense_rating:
        return None

    return {
        team: replace(
            rating,
            attack_rating=rating.attack_rating if variant.use_attack_rating else 1.0,
            defense_rating=rating.defense_rating if variant.use_defense_rating else 1.0,
        )
        for team, rating in ratings.items()
    }


def build_evaluation_probability_rows(
    probabilities: dict[str, dict[str, float]],
    outcomes: list,
    groups: dict[str, list[str]],
) -> list[dict[str, object]]:
    """Build probability rows with extra advancement fields for evaluation."""

    rows = probabilities_to_dataframe(probabilities).to_dict(orient="records")
    teams = [team for group_teams in groups.values() for team in group_teams]
    total = len(outcomes)
    if total == 0:
        raise ValueError("outcomes must not be empty")

    final_counts = {team: 0 for team in teams}
    quarterfinal_counts = {team: 0 for team in teams}
    for outcome in outcomes:
        if outcome.champion in final_counts:
            final_counts[outcome.champion] += 1
        if outcome.runner_up in final_counts:
            final_counts[outcome.runner_up] += 1
        for team in outcome.quarterfinalists:
            quarterfinal_counts[team] += 1

    final_probabilities = {team: count / total for team, count in final_counts.items()}
    quarterfinal_probabilities = {
        team: count / total
        for team, count in quarterfinal_counts.items()
    }

    for row in rows:
        team = str(row["team"])
        row["final_probability"] = final_probabilities[team]
        row["quarterfinal_probability"] = quarterfinal_probabilities[team]

    return rows


@contextmanager
def patched_dynamic_elo_flags(variant: ModelVariant) -> Iterator[None]:
    """Temporarily apply dynamic Elo switches for one variant run."""

    original_group_stage = prediction_config.USE_DYNAMIC_ELO_GROUP_STAGE
    original_knockout = prediction_config.USE_DYNAMIC_ELO_KNOCKOUT
    prediction_config.USE_DYNAMIC_ELO_GROUP_STAGE = variant.use_dynamic_elo_group_stage
    prediction_config.USE_DYNAMIC_ELO_KNOCKOUT = variant.use_dynamic_elo_knockout
    try:
        yield
    finally:
        prediction_config.USE_DYNAMIC_ELO_GROUP_STAGE = original_group_stage
        prediction_config.USE_DYNAMIC_ELO_KNOCKOUT = original_knockout


def write_results(df: pd.DataFrame, output_path: Path) -> None:
    """Persist evaluation results as CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def main() -> None:
    args = parse_args()
    df = evaluate_all_variants(
        simulations=args.simulations,
        seed=args.seed,
        skip_prepare=args.skip_prepare,
    )
    write_results(df, args.output)

    print(f"Results: {args.output}")
    print(f"Rows: {len(df)}")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()

