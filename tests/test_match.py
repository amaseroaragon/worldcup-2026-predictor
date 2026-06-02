from src.prediction.match import MatchResult, sample_poisson, simulate_match


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
    monkeypatch.setattr("src.prediction.match.sample_poisson", lambda lambda_, max_goals=10: 1)

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