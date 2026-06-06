import pandas as pd
import pytest

from scripts.backtesting.combination_experiments import (
    BASELINE_CONFIGURATION,
    build_combination_configurations,
    build_combination_summary,
    export_combination_results,
)


def sample_combination_results() -> pd.DataFrame:
    rows = []
    for tournament in ("world_cup_2018", "world_cup_2022"):
        for code, configuration, brier in (
            ("A", BASELINE_CONFIGURATION, 0.20),
            ("B", "B_better", 0.10),
        ):
            rows.append(
                {
                    "configuration_code": code,
                    "configuration": configuration,
                    "recent_form_weight": 0.15,
                    "squad_strength_weight": 0.30,
                    "dynamic_elo": code == "A",
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
                    "mean_brier_score": brier,
                }
            )
    return pd.DataFrame(rows)


def test_build_combination_configurations_matches_requested_matrix():
    configurations = build_combination_configurations()

    assert [configuration.code for configuration in configurations] == list("ABCDEFGHI")
    assert configurations[0].configuration == BASELINE_CONFIGURATION
    assert configurations[0].dynamic_elo is True
    assert configurations[0].squad_strength_weight == pytest.approx(0.30)
    assert configurations[1].squad_strength_weight == pytest.approx(0.30)
    assert configurations[3].squad_strength_weight == pytest.approx(0.30)
    assert configurations[4].recent_form_weight == pytest.approx(0.20)
    assert configurations[7].squad_strength_weight == pytest.approx(0.35)
    assert configurations[8].squad_strength_weight == pytest.approx(0.40)


def test_build_combination_summary_ranks_and_compares_against_current():
    summary = build_combination_summary(sample_combination_results())
    global_rows = summary[summary["scope"].eq("global")]
    winner = global_rows[global_rows["configuration_rank"].eq(1)].iloc[0]
    baseline = global_rows[global_rows["configuration"].eq(BASELINE_CONFIGURATION)].iloc[0]

    assert winner["configuration"] == "B_better"
    assert winner["mean_brier_improvement_pct_vs_current"] == pytest.approx(50.0)
    assert baseline["mean_brier_delta_vs_current"] == pytest.approx(0.0)


def test_export_combination_results_writes_only_requested_files(tmp_path):
    results = sample_combination_results()
    summary = build_combination_summary(results)
    results_path = tmp_path / "calibration" / "combinations.csv"
    summary_path = tmp_path / "calibration" / "summary.csv"

    export_combination_results(
        results,
        summary,
        results_path=results_path,
        summary_path=summary_path,
    )

    assert results_path.exists()
    assert summary_path.exists()
    assert len(pd.read_csv(results_path)) == 4
    assert len(pd.read_csv(summary_path)) == 6
