from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MatchFixture:
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
    team_a: str
    team_b: str
    goals_a: int
    goals_b: int
    winner: str | None
    is_draw: bool
    decided_by: str
    match_id: str | None = None
    is_real: bool = False


@dataclass
class GroupStandingRow:
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
        return self.goals_for - self.goals_against


@dataclass(frozen=True)
class GroupOutcome:
    group: str
    standings: list[GroupStandingRow]
    winner: str
    runner_up: str
    third_place: str | None = None


@dataclass(frozen=True)
class TournamentOutcome:
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
    n_simulations: int = 1000
    random_seed: int | None = None
    fixed_elo: bool = True
    max_goals: int = 10
