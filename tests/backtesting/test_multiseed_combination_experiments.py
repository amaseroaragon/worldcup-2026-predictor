import pandas as pd
import pytest

from scripts.backtesting.combination_experiments import BASELINE_CONFIGURATION
from scripts.backtesting.multiseed_combination_experiments import (
    add_baseline_comparison,
    build_multiseed_configurations,
    build_multiseed_summary,
    export_multiseed_results,
)


def sample_multiseed_results() -> pd.DataFrame:
    rows = []
    for seed in (1, 7):
        for tournament in ("world_cup_2018", "world_cup_2022"):
            for code, configuration, brier in (
                ("A", BASELINE_CONFIGURATION, 0.20),
                ("I", "I_candidate", 0.10),
            ):
                rows.append(
                    {
                        "configuration_code": code,
                        "configuration": configuration,
                        "recent_form_weight": 0.15,
                        "squad_strength_weight": 0.30 if code == "A" else 0.40,
                        "dynamic_elo": code == "A",
                        "seed": seed,
                        "tournament": tournament,
                        "mean_brier_score": brier,
                        "brier_champion": brier,
                        "brier_final": brier,
                        "brier_semifinal": brier,
                        "brier_quarterfinal": brier,
                        "real_champion_probability": 0.20,
                        "real_champion_rank": 2,
                        "top_3_hit": True,
                        "top_5_hit": True,
                    }
                )
    return add_baseline_comparison(pd.DataFrame(rows))


def test_build_multiseed_configurations_selects_requested_subset():
    configurations = build_multiseed_configurations()

    assert [configuration.code for configuration in configurations] == [
        "A",
        "B",
        "C",
        "D",
        "H",
        "I",
    ]


def test_build_multiseed_summary_aggregates_by_seed_and_ranks():
    summary = build_multiseed_summary(sample_multiseed_results())
    global_rows = summary[summary["tournament"].eq("ALL")]
    winner = global_rows[global_rows["configuration_rank"].eq(1)].iloc[0]
    baseline = global_rows[global_rows["configuration"].eq(BASELINE_CONFIGURATION)].iloc[0]

    assert len(summary) == 6
    assert winner["configuration"] == "I_candidate"
    assert winner["mean_brier_score_mean"] == pytest.approx(0.10)
    assert winner["mean_brier_score_std"] == pytest.approx(0.0)
    assert winner["improvement_pct_vs_baseline_mean"] == pytest.approx(50.0)
    assert baseline["delta_vs_baseline_mean"] == pytest.approx(0.0)


def test_export_multiseed_results_writes_detail_and_summary(tmp_path):
    results = sample_multiseed_results()
    summary = build_multiseed_summary(results)
    results_path = tmp_path / "results.csv"
    summary_path = tmp_path / "summary.csv"

    export_multiseed_results(
        results,
        summary,
        results_path=results_path,
        summary_path=summary_path,
    )

    assert results_path.exists()
    assert summary_path.exists()
    assert len(pd.read_csv(results_path)) == 8
    assert len(pd.read_csv(summary_path)) == 6
