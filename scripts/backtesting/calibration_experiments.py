from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterator

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from scripts.backtesting.evaluate_model_variants import (  # noqa: E402
    BACKTEST_TOURNAMENTS,
    evaluate_variant_for_tournament,
)
from scripts.backtesting.run_backtest import (  # noqa: E402
    build_path_settings,
    prepare_dataset,
    validate_required_inputs,
)
from src.backtesting.model_variants import MODEL_VARIANTS_BY_NAME, ModelVariant  # noqa: E402
from src.prediction.core import poisson  # noqa: E402
from src.prediction.settings import (  # noqa: E402
    DEFAULT_CLI_SEED,
    DEFAULT_N_SIMULATIONS,
    MODEL_WEIGHTS,
)


RESULTS_DIR = Path("data/backtest")
SUMMARY_PATH = RESULTS_DIR / "calibration_summary.csv"

METRIC_COLUMNS = (
    "champion_probability",
    "real_champion_probability",
    "real_champion_rank",
    "top_3_hit",
    "top_5_hit",
    "brier_champion",
    "brier_final",
    "brier_semifinal",
    "brier_quarterfinal",
)

BRIER_COLUMNS = (
    "brier_champion",
    "brier_final",
    "brier_semifinal",
    "brier_quarterfinal",
)


@dataclass(frozen=True)
class CalibrationConfiguration:
    """One controlled FullModel calibration configuration."""

    experiment: str
    configuration: str
    parameter: str
    parameter_value: float | bool
    recent_form_weight: float = MODEL_WEIGHTS.recent_form_weight
    squad_strength_weight: float = MODEL_WEIGHTS.squad_strength_weight
    dynamic_elo_group_stage: bool = True
    dynamic_elo_knockout: bool = True


@dataclass(frozen=True)
class CalibrationExperiment:
    """Declarative calibration experiment and its output destination."""

    name: str
    output_path: Path
    configurations: tuple[CalibrationConfiguration, ...]


def build_calibration_experiments() -> tuple[CalibrationExperiment, ...]:
    """Build the controlled calibration experiments requested for V5.5."""

    recent_form_weights = tuple(i / 100 for i in range(0, 31, 5))
    squad_strength_weights = tuple(i / 100 for i in range(0, 31, 5))

    return (
        CalibrationExperiment(
            name="recent_form_weight",
            output_path=RESULTS_DIR / "recent_form_weight_experiment.csv",
            configurations=tuple(
                CalibrationConfiguration(
                    experiment="recent_form_weight",
                    configuration=f"recent_form_weight={weight:.2f}",
                    parameter="recent_form_weight",
                    parameter_value=weight,
                    recent_form_weight=weight,
                )
                for weight in recent_form_weights
            ),
        ),
        CalibrationExperiment(
            name="squad_strength_weight",
            output_path=RESULTS_DIR / "squad_strength_weight_experiment.csv",
            configurations=tuple(
                CalibrationConfiguration(
                    experiment="squad_strength_weight",
                    configuration=f"squad_strength_weight={weight:.2f}",
                    parameter="squad_strength_weight",
                    parameter_value=weight,
                    squad_strength_weight=weight,
                )
                for weight in squad_strength_weights
            ),
        ),
        CalibrationExperiment(
            name="dynamic_elo",
            output_path=RESULTS_DIR / "dynamic_elo_experiment.csv",
            configurations=(
                CalibrationConfiguration(
                    experiment="dynamic_elo",
                    configuration="dynamic_elo=on",
                    parameter="dynamic_elo",
                    parameter_value=True,
                    dynamic_elo_group_stage=True,
                    dynamic_elo_knockout=True,
                ),
                CalibrationConfiguration(
                    experiment="dynamic_elo",
                    configuration="dynamic_elo=off",
                    parameter="dynamic_elo",
                    parameter_value=False,
                    dynamic_elo_group_stage=False,
                    dynamic_elo_knockout=False,
                ),
            ),
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run controlled FullModel calibration experiments."
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
    parser.add_argument(
        "--skip-prepare",
        action="store_true",
        help="Reuse existing clean results and Elo files in each backtest dataset.",
    )
    return parser.parse_args()


def run_calibration_experiments(
    *,
    simulations: int,
    seed: int,
    skip_prepare: bool,
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Run all calibration experiments and return detail plus summary results."""

    experiments = build_calibration_experiments()
    prepared_paths = {}
    for tournament, dataset_dir in BACKTEST_TOURNAMENTS.items():
        paths = build_path_settings(dataset_dir, output_dir=None)
        validate_required_inputs(paths)
        if not skip_prepare:
            prepare_dataset(paths)
        prepared_paths[tournament] = paths

    results = {}
    for experiment in experiments:
        rows = []
        for configuration in experiment.configurations:
            variant = variant_for_configuration(configuration)
            with patched_model_weights(configuration):
                for tournament, paths in prepared_paths.items():
                    row = evaluate_variant_for_tournament(
                        tournament=tournament,
                        paths=paths,
                        variant=variant,
                        simulations=simulations,
                        seed=seed,
                    )
                    rows.append(
                        {
                            "experiment": configuration.experiment,
                            "configuration": configuration.configuration,
                            "parameter": configuration.parameter,
                            "parameter_value": configuration.parameter_value,
                            "recent_form_weight": configuration.recent_form_weight,
                            "squad_strength_weight": configuration.squad_strength_weight,
                            "dynamic_elo_group_stage": configuration.dynamic_elo_group_stage,
                            "dynamic_elo_knockout": configuration.dynamic_elo_knockout,
                            **row,
                        }
                    )

        results[experiment.name] = pd.DataFrame(rows)

    summary = build_calibration_summary(pd.concat(results.values(), ignore_index=True))
    return results, summary


def variant_for_configuration(configuration: CalibrationConfiguration) -> ModelVariant:
    """Return an isolated FullModel variant for one calibration configuration."""

    full_model = MODEL_VARIANTS_BY_NAME["FullModel"]
    return replace(
        full_model,
        name=configuration.configuration,
        use_dynamic_elo_group_stage=configuration.dynamic_elo_group_stage,
        use_dynamic_elo_knockout=configuration.dynamic_elo_knockout,
    )


@contextmanager
def patched_model_weights(configuration: CalibrationConfiguration) -> Iterator[None]:
    """Temporarily apply calibration weights without changing global defaults."""

    original_recent_form_weight = poisson.RECENT_FORM_WEIGHT
    original_squad_strength_weight = poisson.SQUAD_STRENGTH_WEIGHT
    poisson.RECENT_FORM_WEIGHT = configuration.recent_form_weight
    poisson.SQUAD_STRENGTH_WEIGHT = configuration.squad_strength_weight
    try:
        yield
    finally:
        poisson.RECENT_FORM_WEIGHT = original_recent_form_weight
        poisson.SQUAD_STRENGTH_WEIGHT = original_squad_strength_weight


def build_calibration_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Build tournament-level and global averages with configuration rankings."""

    required_columns = {
        "experiment",
        "configuration",
        "parameter",
        "parameter_value",
        "tournament",
        *METRIC_COLUMNS,
    }
    missing_columns = required_columns - set(results.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing calibration result columns: {missing}")
    if results.empty:
        raise ValueError("results must not be empty")

    group_columns = ["experiment", "configuration", "parameter", "parameter_value"]
    numeric_metrics = list(METRIC_COLUMNS)

    tournament_summary = (
        results.groupby([*group_columns, "tournament"], as_index=False)[numeric_metrics]
        .mean()
        .assign(scope="tournament")
    )
    global_summary = (
        results.groupby(group_columns, as_index=False)[numeric_metrics]
        .mean()
        .assign(scope="global", tournament="ALL")
    )
    summary = pd.concat([tournament_summary, global_summary], ignore_index=True)
    summary["mean_brier_score"] = summary[list(BRIER_COLUMNS)].mean(axis=1)
    summary["configuration_rank"] = (
        summary.groupby(["experiment", "scope", "tournament"])["mean_brier_score"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    return summary.sort_values(
        ["experiment", "scope", "tournament", "configuration_rank", "configuration"]
    ).reset_index(drop=True)


def export_calibration_results(
    results: dict[str, pd.DataFrame],
    summary: pd.DataFrame,
    experiments: tuple[CalibrationExperiment, ...] | None = None,
    summary_path: Path = SUMMARY_PATH,
) -> None:
    """Export independent experiment CSVs and the aggregate summary."""

    experiments = experiments or build_calibration_experiments()
    for experiment in experiments:
        experiment.output_path.parent.mkdir(parents=True, exist_ok=True)
        results[experiment.name].to_csv(experiment.output_path, index=False)

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(summary_path, index=False)


def main() -> None:
    args = parse_args()
    results, summary = run_calibration_experiments(
        simulations=args.simulations,
        seed=args.seed,
        skip_prepare=args.skip_prepare,
    )
    export_calibration_results(results, summary)

    winners = summary[
        (summary["scope"] == "global") & (summary["configuration_rank"] == 1)
    ]
    print(f"Summary: {SUMMARY_PATH}")
    print(f"Detail rows: {sum(len(df) for df in results.values())}")
    print("\nGlobal winners:")
    print(
        winners[
            [
                "experiment",
                "configuration",
                "mean_brier_score",
                "real_champion_probability",
                "real_champion_rank",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()

