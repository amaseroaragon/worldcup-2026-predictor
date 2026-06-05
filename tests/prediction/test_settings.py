from src.elo import config as elo_config
from src.prediction import config as prediction_config
from src.prediction.core.models import SimulationConfig
from src.prediction.io import exports
from src.prediction.metrics import team_strength
from src.prediction.settings import (
    DEFAULT_CLI_SEED,
    DEFAULT_N_SIMULATIONS,
    DEFAULT_TEAM_METRICS_PATH,
    DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH,
    ELO_SETTINGS,
    MODEL_WEIGHTS,
    OUTPUT_SETTINGS,
    PATH_SETTINGS,
    PREDICTION_SETTINGS,
    PROBABILITY_COLUMNS,
    PROBABILITY_VALUE_COLUMNS,
    SIMULATION_SETTINGS,
    TEAM_METRIC_SETTINGS,
)


def test_path_settings_match_public_default_aliases():
    assert PREDICTION_SETTINGS.paths is PATH_SETTINGS
    assert PATH_SETTINGS.world_cup_probabilities_path == DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH
    assert PATH_SETTINGS.team_metrics_path == DEFAULT_TEAM_METRICS_PATH
    assert prediction_config.DEFAULT_WORLD_CUP_2026_GROUPS_PATH == PATH_SETTINGS.groups_path
    assert prediction_config.DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH == (
        PATH_SETTINGS.group_matches_path
    )
    assert prediction_config.DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH == PATH_SETTINGS.knockouts_path
    assert prediction_config.DEFAULT_SQUAD_VALUES_PATH == PATH_SETTINGS.squad_values_path


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
    assert prediction_config.SQUAD_STRENGTH_WEIGHT == MODEL_WEIGHTS.squad_strength_weight == 0.10
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
    assert team_strength.METRICS_VERSION == TEAM_METRIC_SETTINGS.metrics_version == "v4.5"
    assert team_strength.SQUAD_VALUES_SOURCE == (
        TEAM_METRIC_SETTINGS.squad_values_source
    ) == "data/external/teams_value.json"
    assert team_strength.SQUAD_VALUE_UNIT == TEAM_METRIC_SETTINGS.squad_value_unit


def test_output_settings_match_export_aliases():
    assert tuple(exports.PROBABILITY_COLUMNS) == OUTPUT_SETTINGS.probability_columns
    assert exports.PROBABILITY_COLUMNS == PROBABILITY_COLUMNS
    assert exports.PROBABILITY_VALUE_COLUMNS == PROBABILITY_VALUE_COLUMNS
