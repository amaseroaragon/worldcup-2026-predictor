from pathlib import Path

from scripts.backtesting.run_backtest import build_path_settings, load_team_name_mapping


def test_build_path_settings_targets_dataset_and_backtest_outputs(tmp_path):
    dataset = tmp_path / "data" / "backtest" / "world-cup-2022"

    settings = build_path_settings(dataset, output_dir=None)

    assert settings.data_dir == dataset
    assert settings.raw_results_path == dataset / "raw" / "results.csv"
    assert settings.clean_results_path == dataset / "processed" / "clean_results.csv"
    assert settings.elo_history_path == dataset / "processed" / "elo_history.csv"
    assert settings.elo_rankings_path == dataset / "processed" / "elo_rankings.csv"
    assert settings.groups_path == dataset / "external" / "groups.json"
    assert settings.world_cup_probabilities_path == (
        Path("outputs/backtest") / "world-cup-2022" / "world_cup_probabilities.json"
    )


def test_build_path_settings_accepts_explicit_output_dir(tmp_path):
    dataset = tmp_path / "world-cup-2018"
    output_dir = tmp_path / "outputs" / "custom"

    settings = build_path_settings(dataset, output_dir=output_dir)

    assert settings.predictions_output_dir == output_dir
    assert settings.team_metrics_path == output_dir / "team_metrics.json"
    assert settings.tournament_predictions_path == output_dir / "tournament_predictions.json"


def test_load_team_name_mapping_uses_former_to_current_direction(tmp_path):
    path = tmp_path / "former_names.csv"
    path.write_text("current,former\nCountry A,Old Country A\n", encoding="utf-8")

    assert load_team_name_mapping(path) == {"Old Country A": "Country A"}
