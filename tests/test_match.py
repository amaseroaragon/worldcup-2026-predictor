import random

import pytest

from src.prediction.core.match import (
    MatchResult,
    knockout_tiebreaker_probability,
    sample_poisson,
    simulate_match,
)
from src.prediction.core.models import MatchFixture
from src.prediction.metrics.recent_form import RecentFormRating
from src.prediction.metrics.squad_strength import SquadStrengthRating
from src.prediction.metrics.team_strength import TeamStrengthRating


def test_sample_poisson_returns_integer_in_range():
    value = sample_poisson(lambda_=1.35, max_goals=10)

    assert isinstance(value, int)
    assert 0 <= value <= 10


def test_simulate_match_returns_match_result():
    result = simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
    )

    assert isinstance(result, MatchResult)
    assert result.team_a == "Spain"
    assert result.team_b == "France"
    assert result.goals_a >= 0
    assert result.goals_b >= 0


def test_group_stage_match_can_have_draw_or_winner():
    result = simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        knockout=False,
    )

    if result.goals_a == result.goals_b:
        assert result.is_draw is True
        assert result.winner is None
        assert result.decided_by == "draw"
    else:
        assert result.is_draw is False
        assert result.winner in {"Spain", "France"}
        assert result.decided_by == "regular_time"


def test_knockout_match_always_has_winner():
    result = simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        knockout=True,
    )

    assert result.is_draw is False
    assert result.winner in {"Spain", "France"}


def test_knockout_tiebreaker_when_score_is_draw(monkeypatch):
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", lambda lambda_, max_goals=10: 1)

    result = simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        knockout=True,
    )

    assert result.goals_a == 1
    assert result.goals_b == 1
    assert result.winner in {"Spain", "France"}
    assert result.decided_by == "tiebreaker"


def test_knockout_tiebreaker_uses_expected_goals_advantage(monkeypatch):
    class FixedRandom:
        def random(self):
            return 0.53

    def fake_expected_goals_from_elo(elo_a, elo_b, **kwargs):
        return 2.0, 1.0

    def fake_sample_poisson(lambda_, max_goals=10, rng=None):
        return 1

    monkeypatch.setattr("src.prediction.core.match.expected_goals_from_elo", fake_expected_goals_from_elo)
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", fake_sample_poisson)

    result = simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1500,
        elo_b=1500,
        knockout=True,
        rng=FixedRandom(),
    )

    assert result.winner == "Spain"
    assert result.decided_by == "tiebreaker"


def test_knockout_tiebreaker_can_use_elo_only_when_disabled(monkeypatch):
    class FixedRandom:
        def random(self):
            return 0.53

    def fake_expected_goals_from_elo(elo_a, elo_b, **kwargs):
        return 2.0, 1.0

    def fake_sample_poisson(lambda_, max_goals=10, rng=None):
        return 1

    monkeypatch.setattr("src.prediction.core.match.USE_MODEL_BASED_KNOCKOUT_TIEBREAKER", False)
    monkeypatch.setattr("src.prediction.core.match.expected_goals_from_elo", fake_expected_goals_from_elo)
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", fake_sample_poisson)

    result = simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1500,
        elo_b=1500,
        knockout=True,
        rng=FixedRandom(),
    )

    assert result.winner == "France"
    assert result.decided_by == "tiebreaker"


def test_simulate_match_accepts_fixture_and_injected_rng():
    fixture = MatchFixture(
        match_id="A1",
        stage="group",
        group="A",
        team_a="Spain",
        team_b="France",
    )

    result = simulate_match(
        fixture=fixture,
        ratings={"Spain": 1700, "France": 1750},
        rng=random.Random(42),
    )

    assert isinstance(result, MatchResult)
    assert result.match_id == "A1"
    assert result.is_real is False
    assert result.team_a == "Spain"
    assert result.team_b == "France"


def test_knockout_tiebreaker_probability_blends_elo_and_expected_goals():
    probability = knockout_tiebreaker_probability(
        elo_a=1500,
        elo_b=1500,
        expected_goals_a=2.0,
        expected_goals_b=1.0,
    )

    assert probability == pytest.approx((0.65 * 0.5) + (0.35 * (2 / 3)))


def test_knockout_tiebreaker_probability_falls_back_to_elo(monkeypatch):
    monkeypatch.setattr("src.prediction.core.match.USE_MODEL_BASED_KNOCKOUT_TIEBREAKER", False)

    probability = knockout_tiebreaker_probability(
        elo_a=1500,
        elo_b=1500,
        expected_goals_a=2.0,
        expected_goals_b=1.0,
    )

    assert probability == 0.5


def test_simulate_match_uses_team_strength_ratings(monkeypatch):
    expected_goals_arguments = {}

    def fake_expected_goals_from_elo(elo_a, elo_b, **kwargs):
        expected_goals_arguments.update(kwargs)
        return 1.0, 1.0

    monkeypatch.setattr("src.prediction.core.match.expected_goals_from_elo", fake_expected_goals_from_elo)
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", lambda lambda_, max_goals=10: 1)

    simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        team_strength_ratings={
            "Spain": TeamStrengthRating("Spain", 1.2, 0.8, 20),
            "France": TeamStrengthRating("France", 1.1, 0.9, 20),
        },
    )

    assert expected_goals_arguments == {
        "attack_rating_a": 1.2,
        "defense_rating_a": 0.8,
        "attack_rating_b": 1.1,
        "defense_rating_b": 0.9,
        "form_rating_a": None,
        "form_rating_b": None,
        "squad_strength_rating_a": None,
        "squad_strength_rating_b": None,
    }


def test_simulate_match_uses_neutral_strength_for_missing_team_rating(monkeypatch):
    expected_goals_arguments = {}

    def fake_expected_goals_from_elo(elo_a, elo_b, **kwargs):
        expected_goals_arguments.update(kwargs)
        return 1.0, 1.0

    monkeypatch.setattr("src.prediction.core.match.expected_goals_from_elo", fake_expected_goals_from_elo)
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", lambda lambda_, max_goals=10: 1)

    simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        team_strength_ratings={
            "Spain": TeamStrengthRating("Spain", 1.2, 0.8, 20),
        },
    )

    assert expected_goals_arguments["attack_rating_b"] == 1.0
    assert expected_goals_arguments["defense_rating_b"] == 1.0


def test_simulate_match_uses_primary_recent_form_window(monkeypatch):
    expected_goals_arguments = {}

    def fake_expected_goals_from_elo(elo_a, elo_b, **kwargs):
        expected_goals_arguments.update(kwargs)
        return 1.0, 1.0

    monkeypatch.setattr("src.prediction.core.match.expected_goals_from_elo", fake_expected_goals_from_elo)
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", lambda lambda_, max_goals=10: 1)

    simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        recent_form_ratings={
            "Spain": RecentFormRating("Spain", 0.8, 1.15, 1.0, 20),
            "France": RecentFormRating("France", 1.2, None, None, 5),
        },
    )

    assert expected_goals_arguments["form_rating_a"] == 1.15
    assert expected_goals_arguments["form_rating_b"] is None


def test_simulate_match_uses_squad_strength_ratings(monkeypatch):
    expected_goals_arguments = {}

    def fake_expected_goals_from_elo(elo_a, elo_b, **kwargs):
        expected_goals_arguments.update(kwargs)
        return 1.0, 1.0

    monkeypatch.setattr("src.prediction.core.match.expected_goals_from_elo", fake_expected_goals_from_elo)
    monkeypatch.setattr("src.prediction.core.match.sample_poisson", lambda lambda_, max_goals=10: 1)

    simulate_match(
        team_a="Spain",
        team_b="France",
        elo_a=1700,
        elo_b=1750,
        squad_strength_ratings={
            "Spain": SquadStrengthRating("Spain", 1362.5, 1.15),
            "France": SquadStrengthRating("France", 1650.0, 1.15),
        },
    )

    assert expected_goals_arguments["squad_strength_rating_a"] == 1.15
    assert expected_goals_arguments["squad_strength_rating_b"] == 1.15
