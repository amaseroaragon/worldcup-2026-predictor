from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from scripts.backtesting.calibration_experiments import (  # noqa: E402
    BRIER_COLUMNS,
    patched_model_weights,
    variant_for_configuration,
)
from scripts.backtesting.combination_experiments import (  # noqa: E402
    BASELINE_CONFIGURATION,
    CombinationConfiguration,
    build_combination_configurations,
)
from scripts.backtesting.evaluate_model_variants import (  # noqa: E402
    BACKTEST_TOURNAMENTS,
    evaluate_variant_for_tournament,
)
from scripts.backtesting.run_backtest import (  # noqa: E402
    build_path_settings,
    validate_required_inputs,
)
from src.prediction.settings import DEFAULT_N_SIMULATIONS  # noqa: E402


MULTISEED_CONFIGURATION_CODES = ("A", "B", "C", "D", "H", "I")
DEFAULT_SEEDS = (1, 7, 21, 42, 99)
RESULTS_PATH = Path("data/backtest/multiseed_combination_results.csv")
SUMMARY_PATH = Path("data/backtest/multiseed_combination_summary.csv")

SUMMARY_METRICS = (
    "mean_brier_score",
    "brier_champion",
    "brier_final",
    "brier_semifinal",
    "brier_quarterfinal",
    "real_champion_probability",
    "real_champion_rank",
    "top_3_hit",
    "top_5_hit",
    "delta_vs_baseline",
    "improvement_pct_vs_baseline",
)


def build_multiseed_configurations() -> tuple[CombinationConfiguration, ...]:
    """Return the controlled subset selected for multi-seed validation."""

    return tuple(
        configuration
        for configuration in build_combination_configurations()
        if configuration.code in MULTISEED_CONFIGURATION_CODES
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate controlled FullModel combinations across multiple seeds."
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=DEFAULT_N_SIMULATIONS,
        help="Number of Monte Carlo simulations per configuration, seed, and tournament.",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="Random seeds used for stability validation.",
    )
    return parser.parse_args()


def run_multiseed_combination_experiments(
    *,
    simulations: int,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
) -> pd.DataFrame:
    """Evaluate selected combinations for every seed and backtest tournament."""

    if not seeds:
        raise ValueError("seeds must not be empty")

    paths_by_tournament = {}
    for tournament, dataset_dir in BACKTEST_TOURNAMENTS.items():
        paths = build_path_settings(dataset_dir, output_dir=None)
        validate_required_inputs(paths)
        paths_by_tournament[tournament] = paths

    rows = []
    for combination in build_multiseed_configurations():
        configuration = combination.as_calibration_configuration()
        variant = variant_for_configuration(configuration)
        with patched_model_weights(configuration):
            for seed in seeds:
                for tournament, paths in paths_by_tournament.items():
                    evaluation = evaluate_variant_for_tournament(
                        tournament=tournament,
                        paths=paths,
                        variant=variant,
                        simulations=simulations,
                        seed=seed,
                    )
                    row = {
                        "configuration_code": combination.code,
                        "configuration": combination.configuration,
                        "recent_form_weight": combination.recent_form_weight,
                        "squad_strength_weight": combination.squad_strength_weight,
                        "dynamic_elo": combination.dynamic_elo,
                        **evaluation,
                    }
                    row["mean_brier_score"] = sum(
                        float(row[column])
                        for column in BRIER_COLUMNS
                    ) / len(BRIER_COLUMNS)
                    rows.append(row)

    return add_baseline_comparison(pd.DataFrame(rows))


def add_baseline_comparison(results: pd.DataFrame) -> pd.DataFrame:
    """Add paired deltas against baseline A for the same seed and tournament."""

    required_columns = {
        "configuration",
        "seed",
        "tournament",
        "mean_brier_score",
    }
    missing_columns = required_columns - set(results.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing multi-seed result columns: {missing}")
    if results.empty:
        raise ValueError("results must not be empty")

    baseline = results[
        results["configuration"].eq(BASELINE_CONFIGURATION)
    ][["seed", "tournament", "mean_brier_score"]].rename(
        columns={"mean_brier_score": "baseline_mean_brier_score"}
    )
    paired = results.merge(
        baseline,
        on=["seed", "tournament"],
        how="left",
        validate="many_to_one",
    )
    if paired["baseline_mean_brier_score"].isna().any():
        raise ValueError(f"Missing baseline configuration: {BASELINE_CONFIGURATION}")

    paired["delta_vs_baseline"] = (
        paired["mean_brier_score"] - paired["baseline_mean_brier_score"]
    )
    paired["improvement_pct_vs_baseline"] = (
        -paired["delta_vs_baseline"]
        / paired["baseline_mean_brier_score"]
        * 100
    )
    return paired


def build_multiseed_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate tournament and global stability metrics across seeds."""

    required_columns = {
        "configuration_code",
        "configuration",
        "recent_form_weight",
        "squad_strength_weight",
        "dynamic_elo",
        "seed",
        "tournament",
        *SUMMARY_METRICS,
    }
    missing_columns = required_columns - set(results.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing multi-seed summary columns: {missing}")
    if results.empty:
        raise ValueError("results must not be empty")

    configuration_columns = [
        "configuration_code",
        "configuration",
        "recent_form_weight",
        "squad_strength_weight",
        "dynamic_elo",
    ]
    seed_metrics = list(SUMMARY_METRICS)

    tournament_seed_rows = results[
        [*configuration_columns, "tournament", "seed", *seed_metrics]
    ].copy()
    global_seed_rows = (
        results.groupby([*configuration_columns, "seed"], as_index=False)[seed_metrics]
        .mean()
        .assign(tournament="ALL")
    )
    seed_rows = pd.concat([tournament_seed_rows, global_seed_rows], ignore_index=True)

    grouped = seed_rows.groupby([*configuration_columns, "tournament"], as_index=False)
    summary = grouped.agg(
        mean_brier_score_mean=("mean_brier_score", "mean"),
        mean_brier_score_std=("mean_brier_score", "std"),
        brier_champion_mean=("brier_champion", "mean"),
        brier_final_mean=("brier_final", "mean"),
        brier_semifinal_mean=("brier_semifinal", "mean"),
        brier_quarterfinal_mean=("brier_quarterfinal", "mean"),
        real_champion_probability_mean=("real_champion_probability", "mean"),
        real_champion_rank_mean=("real_champion_rank", "mean"),
        top_3_hit_rate=("top_3_hit", "mean"),
        top_5_hit_rate=("top_5_hit", "mean"),
        delta_vs_baseline_mean=("delta_vs_baseline", "mean"),
        improvement_pct_vs_baseline_mean=("improvement_pct_vs_baseline", "mean"),
    )
    summary["configuration_rank"] = (
        summary.groupby("tournament")["mean_brier_score_mean"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    return summary.sort_values(
        ["tournament", "configuration_rank", "configuration_code"]
    ).reset_index(drop=True)


def export_multiseed_results(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    results_path: Path = RESULTS_PATH,
    summary_path: Path = SUMMARY_PATH,
) -> None:
    """Export detailed multi-seed results and aggregate summary."""

    results_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)


def main() -> None:
    args = parse_args()
    results = run_multiseed_combination_experiments(
        simulations=args.simulations,
        seeds=tuple(args.seeds),
    )
    summary = build_multiseed_summary(results)
    export_multiseed_results(results, summary)

    global_ranking = summary[summary["tournament"].eq("ALL")].sort_values(
        "configuration_rank"
    )
    print(f"Results: {RESULTS_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Detail rows: {len(results)}")
    print("\nGlobal multi-seed ranking:")
    print(
        global_ranking[
            [
                "configuration_rank",
                "configuration",
                "mean_brier_score_mean",
                "mean_brier_score_std",
                "improvement_pct_vs_baseline_mean",
                "real_champion_probability_mean",
                "real_champion_rank_mean",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()

