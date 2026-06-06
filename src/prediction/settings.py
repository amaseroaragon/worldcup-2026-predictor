from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class PathSettings:
    project_root: Path = PROJECT_ROOT
    data_dir: Path | None = None
    raw_data_dir: Path | None = None
    external_data_dir: Path | None = None
    processed_data_dir: Path | None = None
    predictions_output_dir: Path = Path("outputs/predictions")
    raw_results_path: Path | None = None
    clean_results_path: Path | None = None
    former_names_path: Path | None = None
    elo_history_path: Path | None = None
    elo_rankings_path: Path | None = None
    groups_path: Path | None = None
    group_matches_path: Path | None = None
    knockouts_path: Path | None = None
    third_place_combinations_path: Path | None = None
    squad_values_path: Path | None = None
    tournament_k_factors_path: Path | None = None
    team_metrics_path: Path | None = None
    tournament_predictions_path: Path | None = None
    world_cup_probabilities_path: Path | None = None

    def __post_init__(self) -> None:
        uses_default_processed_dir = self.data_dir is None and self.processed_data_dir is None
        data_dir = self.data_dir or self.project_root / "data"
        raw_data_dir = self.raw_data_dir or data_dir / "raw"
        external_data_dir = self.external_data_dir or data_dir / "external"
        processed_data_dir = self.processed_data_dir or data_dir / "processed"
        default_elo_history_path = (
            Path("data/processed/elo_history.csv")
            if uses_default_processed_dir
            else processed_data_dir / "elo_history.csv"
        )
        default_elo_rankings_path = (
            Path("data/processed/elo_rankings.csv")
            if uses_default_processed_dir
            else processed_data_dir / "elo_rankings.csv"
        )

        object.__setattr__(self, "data_dir", data_dir)
        object.__setattr__(self, "raw_data_dir", raw_data_dir)
        object.__setattr__(self, "external_data_dir", external_data_dir)
        object.__setattr__(self, "processed_data_dir", processed_data_dir)
        object.__setattr__(
            self,
            "raw_results_path",
            self.raw_results_path or raw_data_dir / "results.csv",
        )
        object.__setattr__(
            self,
            "clean_results_path",
            self.clean_results_path or processed_data_dir / "clean_results.csv",
        )
        object.__setattr__(
            self,
            "former_names_path",
            self.former_names_path or external_data_dir / "former_names.csv",
        )
        object.__setattr__(
            self,
            "elo_history_path",
            self.elo_history_path or default_elo_history_path,
        )
        object.__setattr__(
            self,
            "elo_rankings_path",
            self.elo_rankings_path or default_elo_rankings_path,
        )
        object.__setattr__(
            self,
            "groups_path",
            self.groups_path or external_data_dir / "groups.json",
        )
        object.__setattr__(
            self,
            "group_matches_path",
            self.group_matches_path or external_data_dir / "group_matches.json",
        )
        object.__setattr__(
            self,
            "knockouts_path",
            self.knockouts_path or external_data_dir / "knockouts.json",
        )
        object.__setattr__(
            self,
            "third_place_combinations_path",
            self.third_place_combinations_path
            or external_data_dir / "third_place_combinations.json",
        )
        object.__setattr__(
            self,
            "squad_values_path",
            self.squad_values_path or external_data_dir / "teams_value.json",
        )
        object.__setattr__(
            self,
            "tournament_k_factors_path",
            self.tournament_k_factors_path
            or external_data_dir / "tournament_k_factors.json",
        )
        object.__setattr__(
            self,
            "team_metrics_path",
            self.team_metrics_path or self.predictions_output_dir / "team_metrics.json",
        )
        object.__setattr__(
            self,
            "tournament_predictions_path",
            self.tournament_predictions_path
            or self.predictions_output_dir / "tournament_predictions.json",
        )
        object.__setattr__(
            self,
            "world_cup_probabilities_path",
            self.world_cup_probabilities_path
            or self.predictions_output_dir / "world_cup_probabilities.json",
        )


@dataclass(frozen=True)
class EloSettings:
    base_elo: int = 1500
    k_factor: int = 20
    home_advantage: int = 80
    expected_score_scale: int = 400
    max_margin_of_victory_factor: float = 2.0


@dataclass(frozen=True)
class ModelWeights:
    use_recent_form: bool = True
    recent_form_weight: float = 0.15
    recent_form_primary_window: int = 10
    use_squad_strength: bool = True
    squad_strength_weight: float = 0.30
    use_model_based_knockout_tiebreaker: bool = True
    tiebreaker_expected_goals_weight: float = 0.35
    base_goals: float = 1.35
    elo_sensitivity: float = 0.0015
    min_expected_goals: float = 0.2
    max_expected_goals: float = 3.5
    base_draw_probability: float = 0.26
    draw_probability_decay: float = 0.0008
    min_draw_probability: float = 0.08


@dataclass(frozen=True)
class SimulationSettings:
    n_simulations: int = 1000
    random_seed: int | None = None
    cli_seed: int = 42
    fixed_elo: bool = True
    max_goals: int = 10
    use_dynamic_elo_knockout: bool = True
    use_dynamic_elo_group_stage: bool = True
    teams_per_group: int = 4
    matches_per_group: int = 6


@dataclass(frozen=True)
class TeamMetricSettings:
    metrics_version: str = "v4.5"
    squad_values_source: str = "data/external/teams_value.json"
    squad_value_unit: str = "million_eur"
    recent_matches: int | None = 20
    min_matches: int = 5
    min_rating: float = 0.65
    max_rating: float = 1.45
    squad_min_rating: float = 0.85
    squad_max_rating: float = 1.15
    form_windows: tuple[int, ...] = (5, 10, 20)


@dataclass(frozen=True)
class OutputSettings:
    probability_columns: tuple[str, ...] = (
        "team",
        "champion_probability",
        "runner_up_probability",
        "semifinal_probability",
    )


@dataclass(frozen=True)
class PredictionSettings:
    paths: PathSettings = field(default_factory=PathSettings)
    elo: EloSettings = field(default_factory=EloSettings)
    weights: ModelWeights = field(default_factory=ModelWeights)
    simulation: SimulationSettings = field(default_factory=SimulationSettings)
    team_metrics: TeamMetricSettings = field(default_factory=TeamMetricSettings)
    outputs: OutputSettings = field(default_factory=OutputSettings)


PREDICTION_SETTINGS = PredictionSettings()
PATH_SETTINGS = PREDICTION_SETTINGS.paths
ELO_SETTINGS = PREDICTION_SETTINGS.elo
MODEL_WEIGHTS = PREDICTION_SETTINGS.weights
SIMULATION_SETTINGS = PREDICTION_SETTINGS.simulation
TEAM_METRIC_SETTINGS = PREDICTION_SETTINGS.team_metrics
OUTPUT_SETTINGS = PREDICTION_SETTINGS.outputs

# Public aliases kept for backwards compatibility.
DATA_DIR = PATH_SETTINGS.data_dir
EXTERNAL_DATA_DIR = PATH_SETTINGS.external_data_dir
PROCESSED_DATA_DIR = PATH_SETTINGS.processed_data_dir
RAW_DATA_DIR = PATH_SETTINGS.raw_data_dir
PREDICTIONS_OUTPUT_DIR = PATH_SETTINGS.predictions_output_dir

DEFAULT_WORLD_CUP_2026_GROUPS_PATH = PATH_SETTINGS.groups_path
DEFAULT_WORLD_CUP_2026_GROUP_MATCHES_PATH = PATH_SETTINGS.group_matches_path
DEFAULT_WORLD_CUP_2026_KNOCKOUTS_PATH = PATH_SETTINGS.knockouts_path
DEFAULT_WORLD_CUP_2026_THIRD_PLACE_COMBINATIONS_PATH = (
    PATH_SETTINGS.third_place_combinations_path
)
DEFAULT_SQUAD_VALUES_PATH = PATH_SETTINGS.squad_values_path
DEFAULT_TOURNAMENT_K_FACTORS_PATH = PATH_SETTINGS.tournament_k_factors_path
DEFAULT_RAW_RESULTS_PATH = PATH_SETTINGS.raw_results_path
DEFAULT_ELO_RANKINGS_PATH = PATH_SETTINGS.elo_rankings_path
DEFAULT_ELO_HISTORY_PATH = PATH_SETTINGS.elo_history_path
DEFAULT_CLEAN_RESULTS_PATH = PATH_SETTINGS.clean_results_path
DEFAULT_FORMER_NAMES_PATH = PATH_SETTINGS.former_names_path
DEFAULT_TEAM_METRICS_PATH = PATH_SETTINGS.team_metrics_path
DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH = PATH_SETTINGS.tournament_predictions_path
DEFAULT_WORLD_CUP_PROBABILITIES_JSON_PATH = PATH_SETTINGS.world_cup_probabilities_path

BASE_ELO = ELO_SETTINGS.base_elo
K_FACTOR = ELO_SETTINGS.k_factor
HOME_ADVANTAGE = ELO_SETTINGS.home_advantage
ELO_EXPECTED_SCORE_SCALE = ELO_SETTINGS.expected_score_scale
MAX_MARGIN_OF_VICTORY_FACTOR = ELO_SETTINGS.max_margin_of_victory_factor

TEAMS_PER_GROUP = SIMULATION_SETTINGS.teams_per_group
MATCHES_PER_GROUP = SIMULATION_SETTINGS.matches_per_group
DEFAULT_N_SIMULATIONS = SIMULATION_SETTINGS.n_simulations
DEFAULT_CLI_SEED = SIMULATION_SETTINGS.cli_seed
DEFAULT_FIXED_ELO = SIMULATION_SETTINGS.fixed_elo
DEFAULT_MAX_GOALS = SIMULATION_SETTINGS.max_goals

USE_RECENT_FORM = MODEL_WEIGHTS.use_recent_form
RECENT_FORM_WEIGHT = MODEL_WEIGHTS.recent_form_weight
RECENT_FORM_PRIMARY_WINDOW = MODEL_WEIGHTS.recent_form_primary_window
USE_SQUAD_STRENGTH = MODEL_WEIGHTS.use_squad_strength
SQUAD_STRENGTH_WEIGHT = MODEL_WEIGHTS.squad_strength_weight
USE_MODEL_BASED_KNOCKOUT_TIEBREAKER = MODEL_WEIGHTS.use_model_based_knockout_tiebreaker
TIEBREAKER_EXPECTED_GOALS_WEIGHT = MODEL_WEIGHTS.tiebreaker_expected_goals_weight
BASE_DRAW_PROBABILITY = MODEL_WEIGHTS.base_draw_probability
DRAW_PROBABILITY_DECAY = MODEL_WEIGHTS.draw_probability_decay
MIN_DRAW_PROBABILITY = MODEL_WEIGHTS.min_draw_probability
USE_DYNAMIC_ELO_KNOCKOUT = SIMULATION_SETTINGS.use_dynamic_elo_knockout
USE_DYNAMIC_ELO_GROUP_STAGE = SIMULATION_SETTINGS.use_dynamic_elo_group_stage

METRICS_VERSION = TEAM_METRIC_SETTINGS.metrics_version
SQUAD_VALUES_SOURCE = TEAM_METRIC_SETTINGS.squad_values_source
SQUAD_VALUE_UNIT = TEAM_METRIC_SETTINGS.squad_value_unit
TEAM_STRENGTH_RECENT_MATCHES = TEAM_METRIC_SETTINGS.recent_matches
TEAM_STRENGTH_MIN_MATCHES = TEAM_METRIC_SETTINGS.min_matches
TEAM_STRENGTH_MIN_RATING = TEAM_METRIC_SETTINGS.min_rating
TEAM_STRENGTH_MAX_RATING = TEAM_METRIC_SETTINGS.max_rating
SQUAD_STRENGTH_MIN_RATING = TEAM_METRIC_SETTINGS.squad_min_rating
SQUAD_STRENGTH_MAX_RATING = TEAM_METRIC_SETTINGS.squad_max_rating
FORM_WINDOWS = TEAM_METRIC_SETTINGS.form_windows

PROBABILITY_COLUMNS = list(OUTPUT_SETTINGS.probability_columns)
PROBABILITY_VALUE_COLUMNS = PROBABILITY_COLUMNS[1:]
