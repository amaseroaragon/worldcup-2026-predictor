import pytest

from src.prediction.monte_carlo import run_monte_carlo


def mini_groups() -> dict[str, list[str]]:
    return {
        "A": ["Team 1", "Team 2", "Team 3", "Team 4"],
        "B": ["Team 5", "Team 6", "Team 7", "Team 8"],
        "C": ["Team 9", "Team 10", "Team 11", "Team 12"],
        "D": ["Team 13", "Team 14", "Team 15", "Team 16"],
    }


def mini_ratings(groups: dict[str, list[str]]) -> dict[str, float]:
    return {
        team: 1800.0 - index * 20
        for index, team in enumerate(team for teams in groups.values() for team in teams)
    }


def test_run_monte_carlo_returns_dict():
    groups = mini_groups()

    result = run_monte_carlo(groups, mini_ratings(groups), simulations=5, seed=42)

    assert isinstance(result, dict)


def test_run_monte_carlo_probabilities_are_between_zero_and_one():
    groups = mini_groups()

    result = run_monte_carlo(groups, mini_ratings(groups), simulations=5, seed=42)

    for probabilities in result.values():
        assert 0 <= probabilities["champion"] <= 1
        assert 0 <= probabilities["runner_up"] <= 1
        assert 0 <= probabilities["semifinal"] <= 1


def test_run_monte_carlo_is_reproducible_with_same_seed():
    groups = mini_groups()
    ratings = mini_ratings(groups)

    result_a = run_monte_carlo(groups, ratings, simulations=10, seed=42)
    result_b = run_monte_carlo(groups, ratings, simulations=10, seed=42)

    assert result_a == result_b


def test_run_monte_carlo_rejects_invalid_simulations():
    groups = mini_groups()

    with pytest.raises(ValueError, match="simulations"):
        run_monte_carlo(groups, mini_ratings(groups), simulations=0)


def test_run_monte_carlo_includes_existing_teams_in_output():
    groups = mini_groups()

    result = run_monte_carlo(groups, mini_ratings(groups), simulations=5, seed=42)

    assert set(result) == {team for teams in groups.values() for team in teams}


def test_run_monte_carlo_champion_probabilities_sum_to_one():
    groups = mini_groups()

    result = run_monte_carlo(groups, mini_ratings(groups), simulations=10, seed=42)

    champion_probability_sum = sum(probabilities["champion"] for probabilities in result.values())

    assert champion_probability_sum == pytest.approx(1.0)
