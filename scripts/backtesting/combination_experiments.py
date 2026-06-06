from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from scripts.backtesting.calibration_experiments import (  # noqa: E402
    BRIER_COLUMNS,
    METRIC_COLUMNS,
    CalibrationConfiguration,
    patched_model_weights,
    variant_for_configuration,
)
from scripts.backtesting.evaluate_model_variants import (  # noqa: E402
    BACKTEST_TOURNAMENTS,
    evaluate_variant_for_tournament,
)
from scripts.backtesting.run_backtest import (  # noqa: E402
    build_path_settings,
    validate_required_inputs,
)
from src.prediction.settings import DEFAULT_CLI_SEED, DEFAULT_N_SIMULATIONS  # noqa: E402


RESULTS_DIR = Path("data/backtest")
RESULTS_PATH = RESULTS_DIR / "combination_experiments.csv"
SUMMARY_PATH = RESULTS_DIR / "combination_summary.csv"
BASELINE_CONFIGURATION = "A_FullModel_current"


@dataclass(frozen=True)
class CombinationConfiguration:
    """Named controlled combination for the second calibration round."""

    code: str
    name: str
    recent_form_weight: float
    squad_strength_weight: float
    dynamic_elo: bool

    @property
    def configuration(self) -> str:
        return f"{self.code}_{self.name}"

    def as_calibration_configuration(self) -> CalibrationConfiguration:
        return CalibrationConfiguration(
            experiment="controlled_combinations",
            configuration=self.configuration,
            parameter="combination",
            parameter_value=self.code,
            recent_form_weight=self.recent_form_weight,
            squad_strength_weight=self.squad_strength_weight,
            dynamic_elo_group_stage=self.dynamic_elo,
            dynamic_elo_knockout=self.dynamic_elo,
        )


def build_combination_configurations() -> tuple[CombinationConfiguration, ...]:
    """Return the nine controlled combinations requested for calibration round two."""

    return (
        CombinationConfiguration("A", "FullModel_current", 0.15, 0.30, True),
        CombinationConfiguration("B", "FullModel_dynamic_off", 0.15, 0.30, False),
        CombinationConfiguration("C", "FullModel_squad_0.30", 0.15, 0.30, True),
        CombinationConfiguration(
            "D",
            "FullModel_squad_0.30_dynamic_off",
            0.15,
            0.30,
            False,
        ),
        CombinationConfiguration(
            "E",
            "FullModel_recent_0.20_squad_0.30_dynamic_off",
            0.20,
            0.30,
            False,
        ),
        CombinationConfiguration(
            "F",
            "FullModel_recent_0.05_squad_0.30_dynamic_off",
            0.05,
            0.30,
            False,
        ),
        CombinationConfiguration(
            "G",
            "FullModel_recent_0.00_squad_0.30_dynamic_off",
            0.00,
            0.30,
            False,
        ),
        CombinationConfiguration(
            "H",
            "FullModel_squad_0.35_dynamic_off",
            0.15,
            0.35,
            False,
        ),
        CombinationConfiguration(
            "I",
            "FullModel_squad_0.40_dynamic_off",
            0.15,
            0.40,
            False,
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run controlled FullModel combination calibration experiments."
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=DEFAULT_N_SIMULATIONS,
        help="Number of Monte Carlo simulations per configuration and tournament.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_CLI_SEED,
        help="Random seed for reproducible simulations.",
    )
    return parser.parse_args()


def run_combination_experiments(*, simulations: int, seed: int) -> pd.DataFrame:
    """Evaluate every controlled combination against all backtest tournaments."""

    paths_by_tournament = {}
    for tournament, dataset_dir in BACKTEST_TOURNAMENTS.items():
        paths = build_path_settings(dataset_dir, output_dir=None)
        validate_required_inputs(paths)
        paths_by_tournament[tournament] = paths

    rows = []
    for combination in build_combination_configurations():
        configuration = combination.as_calibration_configuration()
        variant = variant_for_configuration(configuration)
        with patched_model_weights(configuration):
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

    return pd.DataFrame(rows)


def build_combination_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Build tournament/global rankings and deltas against FullModel current."""

    required_columns = {
        "configuration_code",
        "configuration",
        "recent_form_weight",
        "squad_strength_weight",
        "dynamic_elo",
        "tournament",
        "mean_brier_score",
        *METRIC_COLUMNS,
    }
    missing_columns = required_columns - set(results.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing combination result columns: {missing}")
    if results.empty:
        raise ValueError("results must not be empty")

    configuration_columns = [
        "configuration_code",
        "configuration",
        "recent_form_weight",
        "squad_strength_weight",
        "dynamic_elo",
    ]
    numeric_metrics = [*METRIC_COLUMNS, "mean_brier_score"]
    tournament_summary = (
        results.groupby([*configuration_columns, "tournament"], as_index=False)[numeric_metrics]
        .mean()
        .assign(scope="tournament")
    )
    global_summary = (
        results.groupby(configuration_columns, as_index=False)[numeric_metrics]
        .mean()
        .assign(scope="global", tournament="ALL")
    )
    summary = pd.concat([tournament_summary, global_summary], ignore_index=True)
    summary["configuration_rank"] = (
        summary.groupby(["scope", "tournament"])["mean_brier_score"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    baseline = summary[
        summary["configuration"].eq(BASELINE_CONFIGURATION)
    ][["scope", "tournament", "mean_brier_score"]].rename(
        columns={"mean_brier_score": "baseline_mean_brier_score"}
    )
    summary = summary.merge(baseline, on=["scope", "tournament"], how="left", validate="many_to_one")
    if summary["baseline_mean_brier_score"].isna().any():
        raise ValueError(f"Missing baseline configuration: {BASELINE_CONFIGURATION}")

    summary["mean_brier_delta_vs_current"] = (
        summary["mean_brier_score"] - summary["baseline_mean_brier_score"]
    )
    summary["mean_brier_improvement_pct_vs_current"] = (
        -summary["mean_brier_delta_vs_current"]
        / summary["baseline_mean_brier_score"]
        * 100
    )

    return summary.sort_values(
        ["scope", "tournament", "configuration_rank", "configuration_code"]
    ).reset_index(drop=True)


def export_combination_results(
    results: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    results_path: Path = RESULTS_PATH,
    summary_path: Path = SUMMARY_PATH,
) -> None:
    """Export combination detail and summary CSVs."""

    results_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(results_path, index=False)
    summary.to_csv(summary_path, index=False)


def main() -> None:
    args = parse_args()
    results = run_combination_experiments(
        simulations=args.simulations,
        seed=args.seed,
    )
    summary = build_combination_summary(results)
    export_combination_results(results, summary)

    global_ranking = summary[summary["scope"].eq("global")].sort_values(
        "configuration_rank"
    )
    print(f"Results: {RESULTS_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Detail rows: {len(results)}")
    print("\nGlobal ranking:")
    print(
        global_ranking[
            [
                "configuration_rank",
                "configuration",
                "mean_brier_score",
                "mean_brier_improvement_pct_vs_current",
                "real_champion_probability",
                "real_champion_rank",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
