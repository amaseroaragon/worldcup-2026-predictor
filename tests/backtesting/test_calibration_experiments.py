from pathlib import Path

import pandas as pd
import pytest

from scripts.backtesting.calibration_experiments import (
    CalibrationExperiment,
    build_calibration_experiments,
    build_calibration_summary,
    export_calibration_results,
)


def sample_results() -> pd.DataFrame:
    rows = []
    for tournament in ("world_cup_2018", "world_cup_2022"):
        for configuration, brier in (("weight=0.10", 0.10), ("weight=0.20", 0.20)):
            rows.append(
                {
                    "experiment": "sample",
                    "configuration": configuration,
                    "parameter": "weight",
                    "parameter_value": float(configuration[-4:]),
                    "tournament": tournament,
                    "champion_probability": 0.30,
                    "real_champion_probability": 0.20,
                    "real_champion_rank": 2,
                    "top_3_hit": True,
                    "top_5_hit": True,
                    "brier_champion": brier,
                    "brier_final": brier,
                    "brier_semifinal": brier,
                    "brier_quarterfinal": brier,
                }
            )
    return pd.DataFrame(rows)


def test_build_calibration_experiments_generates_requested_configurations():
    experiments = {experiment.name: experiment for experiment in build_calibration_experiments()}

    assert [config.parameter_value for config in experiments["recent_form_weight"].configurations] == [
        0.00,
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
    ]
    assert len(experiments["squad_strength_weight"].configurations) == 7
    assert [
        config.parameter_value
        for config in experiments["dynamic_elo"].configurations
    ] == [True, False]


def test_build_calibration_summary_adds_global_average_and_ranking():
    summary = build_calibration_summary(sample_results())
    global_rows = summary[summary["scope"] == "global"]
    winner = global_rows[global_rows["configuration_rank"] == 1].iloc[0]

    assert len(summary[summary["scope"] == "tournament"]) == 4
    assert len(global_rows) == 2
    assert winner["configuration"] == "weight=0.10"
    assert winner["mean_brier_score"] == pytest.approx(0.10)


def test_export_calibration_results_writes_detail_and_summary_csvs(tmp_path):
    results = {"sample": sample_results()}
    summary = build_calibration_summary(results["sample"])
    detail_path = tmp_path / "sample.csv"
    summary_path = tmp_path / "summary.csv"
    experiments = (
        CalibrationExperiment(
            name="sample",
            output_path=detail_path,
            configurations=(),
        ),
    )

    export_calibration_results(
        results,
        summary,
        experiments=experiments,
        summary_path=summary_path,
    )

    assert detail_path.exists()
    assert summary_path.exists()
    assert len(pd.read_csv(detail_path)) == 4
    assert len(pd.read_csv(summary_path)) == 6

