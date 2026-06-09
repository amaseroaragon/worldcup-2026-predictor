from src.elo import config as elo_config
from src.prediction import config as prediction_config
from src.prediction import pipeline
from src.prediction.core.models import SimulationConfig
from src.prediction.io import exports
from src.prediction.metrics import team_strength
from src.prediction.settings import (
    DEFAULT_CLI_SEED,
    DEFAULT_CLEAN_RESULTS_PATH,
    DEFAULT_ELO_HISTORY_PATH,
    DEFAULT_ELO_RANKINGS_PATH,
    DEFAULT_FORMER_NAMES_PATH,
    DEFAULT_N_SIMULATIONS,
    DEFAULT_RAW_RESULTS_PATH,
    DEFAULT_TEAM_METRICS_PATH,
    DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
    DISPLAY_SETTINGS,
    DRAW_COMPETITIVE_MARGIN,
    ELO_SETTINGS,
    MODEL_WEIGHTS,
    OUTPUT_SETTINGS,
    PATH_SETTINGS,
    PREDICTION_SETTINGS,
    PathSettings,
    PROBABILITY_COLUMNS,
    PROBABILITY_VALUE_COLUMNS,
    SIMULATION_SETTINGS,
    TEAM_METRIC_SETTINGS,
)


def test_path_settings_match_public_default_aliases():
    assert PREDICTION_SETTINGS.paths is PATH_SETTINGS
    assert PATH_SETTINGS.raw_results_path == DEFAULT_RAW_RESULTS_PATH
    assert PATH_SETTINGS.clean_results_path == DEFAULT_CLEAN_RESULTS_PATH
    assert PATH_SETTINGS.former_names_path == DEFAULT_FORMER_NAMES_PATH
    assert PATH_SETTINGS.elo_history_path == DEFAULT_ELO_HISTORY_PATH
    assert PATH_SETTINGS.elo_rankings_path == DEFAULT_ELO_RANKINGS_PATH
    assert PATH_SETTINGS.world_cup_probabilities_path == DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH
    assert PATH_SETTINGS.team_metrics_path == DEFAULT_TEAM_METRICS_PATH
    assert prediction_config.DEFAULT_WORLD_CUP_2026_GROUPS_PATH == PATH_SETTINGS.groups_path
    assert prediction_config.DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH == (
        PATH_SETTINGS.group_matches_path
    )
    assert prediction_config.DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH == PATH_SETTINGS.knockouts_path
    assert prediction_config.DEFAULT_SQUAD_VALUES_PATH == PATH_SETTINGS.squad_values_path


def test_display_settings_expose_competitive_draw_margin():
    assert PREDICTION_SETTINGS.display is DISPLAY_SETTINGS
    assert DRAW_COMPETITIVE_MARGIN == DISPLAY_SETTINGS.draw_competitive_margin == 0.05


def test_path_settings_keep_current_default_routes():
    assert PATH_SETTINGS.raw_results_path.as_posix().endswith("data/raw/results.csv")
    assert PATH_SETTINGS.clean_results_path.as_posix().endswith(
        "data/processed/clean_results.csv"
    )
    assert PATH_SETTINGS.former_names_path.as_posix().endswith(
        "data/external/former_names.csv"
    )
    assert PATH_SETTINGS.groups_path.as_posix().endswith("data/external/groups.json")
    assert PATH_SETTINGS.group_matches_path.as_posix().endswith(
        "data/external/group_matches.json"
    )
    assert PATH_SETTINGS.knockouts_path.as_posix().endswith("data/external/knockouts.json")
    assert PATH_SETTINGS.third_place_combinations_path.as_posix().endswith(
        "data/external/third_place_combinations.json"
    )
    assert PATH_SETTINGS.squad_values_path.as_posix().endswith(
        "data/external/teams_value.json"
    )
    assert PATH_SETTINGS.tournament_k_factors_path.as_posix().endswith(
        "data/external/tournament_k_factors.json"
    )
    assert PATH_SETTINGS.elo_history_path.as_posix() == "data/processed/elo_history.csv"
    assert PATH_SETTINGS.elo_rankings_path.as_posix() == "data/processed/elo_rankings.csv"
    assert PATH_SETTINGS.team_metrics_path.as_posix() == (
        "outputs/predictions/team_metrics.json"
    )


def test_path_settings_can_target_an_alternative_dataset(tmp_path):
    dataset_dir = tmp_path / "backtest" / "world_cup_2018"
    settings = PathSettings(
        data_dir=dataset_dir,
        predictions_output_dir=tmp_path / "outputs" / "world_cup_2018",
    )

    assert settings.raw_results_path == dataset_dir / "raw" / "results.csv"
    assert settings.clean_results_path == dataset_dir / "processed" / "clean_results.csv"
    assert settings.former_names_path == dataset_dir / "external" / "former_names.csv"
    assert settings.groups_path == dataset_dir / "external" / "groups.json"
    assert settings.group_matches_path == dataset_dir / "external" / "group_matches.json"
    assert settings.knockouts_path == dataset_dir / "external" / "knockouts.json"
    assert settings.third_place_combinations_path == (
        dataset_dir / "external" / "third_place_combinations.json"
    )
    assert settings.squad_values_path == dataset_dir / "external" / "teams_value.json"
    assert settings.tournament_k_factors_path == (
        dataset_dir / "external" / "tournament_k_factors.json"
    )
    assert settings.elo_history_path == dataset_dir / "processed" / "elo_history.csv"
    assert settings.elo_rankings_path == dataset_dir / "processed" / "elo_rankings.csv"
    assert settings.team_metrics_path == (
        tmp_path / "outputs" / "world_cup_2018" / "team_metrics.json"
    )


def test_path_settings_accept_explicit_file_overrides(tmp_path):
    settings = PathSettings(
        raw_results_path=tmp_path / "results_2018.csv",
        clean_results_path=tmp_path / "clean_2018.csv",
        groups_path=tmp_path / "groups_2018.json",
    )

    assert settings.raw_results_path == tmp_path / "results_2018.csv"
    assert settings.clean_results_path == tmp_path / "clean_2018.csv"
    assert settings.groups_path == tmp_path / "groups_2018.json"


def test_prediction_input_loader_accepts_path_settings(monkeypatch, tmp_path):
    settings = PathSettings(
        data_dir=tmp_path / "backtest" / "world_cup_2022",
        predictions_output_dir=tmp_path / "outputs" / "world_cup_2022",
    )
    calls = {}

    def capture(name):
        def inner(path):
            calls[name] = path
            return {}

        return inner

    monkeypatch.setattr(pipeline, "load_ratings", capture("elo_rankings_path"))
    monkeypatch.setattr(pipeline.pd, "read_csv", lambda path: calls.setdefault("results_path", path))
    monkeypatch.setattr(
        pipeline,
        "build_team_strength_ratings",
        lambda results, elo_ratings: {},
    )
    monkeypatch.setattr(pipeline, "build_recent_form_ratings", lambda results: {})
    monkeypatch.setattr(pipeline, "load_squad_values", capture("squad_values_path"))
    monkeypatch.setattr(pipeline, "build_squad_strength_ratings", lambda squad_values: {})
    monkeypatch.setattr(pipeline, "load_groups_config", capture("groups_path"))
    monkeypatch.setattr(pipeline, "load_group_matches_config", capture("group_matches_path"))
    monkeypatch.setattr(pipeline, "load_knockouts_config", capture("knockouts_path"))
    monkeypatch.setattr(
        pipeline,
        "load_third_place_combinations_config",
        capture("third_place_combinations_path"),
    )

    pipeline.load_prediction_inputs(path_settings=settings)

    assert calls["elo_rankings_path"] == settings.elo_rankings_path
    assert calls["results_path"] == settings.clean_results_path
    assert calls["squad_values_path"] == settings.squad_values_path
    assert calls["groups_path"] == settings.groups_path
    assert calls["group_matches_path"] == settings.group_matches_path
    assert calls["knockouts_path"] == settings.knockouts_path
    assert calls["third_place_combinations_path"] == settings.third_place_combinations_path


def test_prediction_input_loader_can_allow_missing_third_place_combinations(
    monkeypatch,
    tmp_path,
):
    settings = PathSettings(data_dir=tmp_path / "backtest" / "world_cup_2018")
    calls = {}

    monkeypatch.setattr(pipeline, "load_ratings", lambda path: {})
    monkeypatch.setattr(pipeline.pd, "read_csv", lambda path: calls.setdefault("results", path))
    monkeypatch.setattr(
        pipeline,
        "build_team_strength_ratings",
        lambda results, elo_ratings: {},
    )
    monkeypatch.setattr(pipeline, "build_recent_form_ratings", lambda results: {})
    monkeypatch.setattr(pipeline, "load_squad_values", lambda path: {})
    monkeypatch.setattr(pipeline, "build_squad_strength_ratings", lambda squad_values: {})
    monkeypatch.setattr(pipeline, "load_groups_config", lambda path: {})
    monkeypatch.setattr(pipeline, "load_group_matches_config", lambda path: [])
    monkeypatch.setattr(pipeline, "load_knockouts_config", lambda path: [])
    monkeypatch.setattr(
        pipeline,
        "load_third_place_combinations_config",
        lambda path: calls.setdefault("third_place_combinations", path),
    )

    inputs = pipeline.load_prediction_inputs(
        path_settings=settings,
        allow_missing_third_place_combinations=True,
    )

    assert inputs.third_place_combinations == {}
    assert "third_place_combinations" not in calls


def test_elo_settings_match_legacy_elo_config_aliases():
    assert elo_config.BASE_ELO == ELO_SETTINGS.base_elo == 1500
    assert elo_config.K_FACTOR == ELO_SETTINGS.k_factor == 20
    assert elo_config.HOME_ADVANTAGE == ELO_SETTINGS.home_advantage == 80
    assert elo_config.ELO_EXPECTED_SCORE_SCALE == ELO_SETTINGS.expected_score_scale == 400
    assert elo_config.MAX_MARGIN_OF_VICTORY_FACTOR == (
        ELO_SETTINGS.max_margin_of_victory_factor
    ) == 2.0


def test_model_weight_aliases_keep_current_values():
    assert prediction_config.USE_RECENT_FORM is MODEL_WEIGHTS.use_recent_form is True
    assert prediction_config.RECENT_FORM_WEIGHT == MODEL_WEIGHTS.recent_form_weight == 0.15
    assert prediction_config.RECENT_FORM_PRIMARY_WINDOW == (
        MODEL_WEIGHTS.recent_form_primary_window
    ) == 10
    assert prediction_config.USE_SQUAD_STRENGTH is MODEL_WEIGHTS.use_squad_strength is True
    assert prediction_config.SQUAD_STRENGTH_WEIGHT == MODEL_WEIGHTS.squad_strength_weight == 0.30
    assert prediction_config.TIEBREAKER_EXPECTED_GOALS_WEIGHT == (
        MODEL_WEIGHTS.tiebreaker_expected_goals_weight
    ) == 0.35
    assert MODEL_WEIGHTS.base_draw_probability == 0.26
    assert MODEL_WEIGHTS.draw_probability_decay == 0.0008
    assert MODEL_WEIGHTS.min_draw_probability == 0.08
    assert MODEL_WEIGHTS.base_goals == 1.35
    assert MODEL_WEIGHTS.elo_sensitivity == 0.0015
    assert MODEL_WEIGHTS.min_expected_goals == 0.2
    assert MODEL_WEIGHTS.max_expected_goals == 3.5


def test_simulation_settings_match_existing_defaults():
    config = SimulationConfig()

    assert DEFAULT_N_SIMULATIONS == SIMULATION_SETTINGS.n_simulations == 1000
    assert DEFAULT_CLI_SEED == SIMULATION_SETTINGS.cli_seed == 42
    assert config.n_simulations == SIMULATION_SETTINGS.n_simulations
    assert config.random_seed == SIMULATION_SETTINGS.random_seed
    assert config.fixed_elo == SIMULATION_SETTINGS.fixed_elo is True
    assert config.max_goals == SIMULATION_SETTINGS.max_goals == 10
    assert prediction_config.TEAMS_PER_GROUP == SIMULATION_SETTINGS.teams_per_group == 4


def test_team_metric_settings_match_legacy_aliases():
    assert team_strength.METRICS_VERSION == TEAM_METRIC_SETTINGS.metrics_version == "v5.0"
    assert team_strength.SQUAD_VALUES_SOURCE == (
        TEAM_METRIC_SETTINGS.squad_values_source
    ) == "data/external/teams_value.json"
    assert team_strength.SQUAD_VALUE_UNIT == TEAM_METRIC_SETTINGS.squad_value_unit
    assert team_strength.TEAM_STRENGTH_RECENT_MATCHES == (
        TEAM_METRIC_SETTINGS.recent_matches
    ) == 20


def test_output_settings_match_export_aliases():
    assert tuple(exports.PROBABILITY_COLUMNS) == OUTPUT_SETTINGS.probability_columns
    assert exports.PROBABILITY_COLUMNS == PROBABILITY_COLUMNS
    assert exports.PROBABILITY_VALUE_COLUMNS == PROBABILITY_VALUE_COLUMNS
