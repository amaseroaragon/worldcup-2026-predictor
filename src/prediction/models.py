from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MatchFixture:
    """Scheduled or resolved match metadata."""

    match_id: str
    stage: str
    team_a: str
    team_b: str
    group: str | None = None
    source_a: str | None = None
    source_b: str | None = None
    date: str | None = None


@dataclass(frozen=True)
class MatchResult:
    """Simulated or real result for a single match."""

    team_a: str
    team_b: str
    goals_a: int
    goals_b: int
    winner: str | None
    is_draw: bool
    decided_by: str
    match_id: str | None = None
    is_real: bool = False


@dataclass(frozen=True)
class MatchPrediction:
    """Persistable prediction record for a single match."""

    match_id: str
    stage: str
    group: str | None
    round: str | None
    home_team: str
    away_team: str
    predicted_home_goals: int
    predicted_away_goals: int
    predicted_winner: str | None
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    user_home_goals: int | None = None
    user_away_goals: int | None = None
    real_home_goals: int | None = None
    real_away_goals: int | None = None
    prediction_correct: bool | None = None


@dataclass
class GroupStandingRow:
    """Mutable standings row for one team in a group."""

    team: str
    played: int = 0
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0

    @property
    def goal_difference(self) -> int:
        """Return goals scored minus goals conceded."""

        return self.goals_for - self.goals_against


@dataclass(frozen=True)
class GroupOutcome:
    """Final standings and qualifiers for one group."""

    group: str
    standings: list[GroupStandingRow]
    winner: str
    runner_up: str
    third_place: str | None = None
    match_results: list[MatchResult] = field(default_factory=list)


@dataclass(frozen=True)
class TournamentOutcome:
    """Summary of one complete tournament simulation."""

    champion: str | None = None
    runner_up: str | None = None
    semifinalists: set[str] = field(default_factory=set)
    quarterfinalists: set[str] = field(default_factory=set)
    round_of_16: set[str] = field(default_factory=set)
    round_of_32: set[str] = field(default_factory=set)
    group_stage_eliminated: set[str] = field(default_factory=set)
    group_outcomes: dict[str, GroupOutcome] = field(default_factory=dict)
    match_results: list[MatchResult] = field(default_factory=list)


@dataclass(frozen=True)
class SimulationConfig:
    """Runtime options for match and tournament simulation."""

    n_simulations: int = 1000
    random_seed: int | None = None
    fixed_elo: bool = True
    max_goals: int = 10
