from src.elo.config import K_FACTOR
from src.elo.context import MatchContext, get_k_factor, load_tournament_k_factors
from src.elo.update import match_result, margin_of_victory_factor, update_rating


def test_get_k_factor_defaults_to_existing_fixed_k():
    assert get_k_factor() == K_FACTOR


def test_get_k_factor_uses_tournament_mapping():
    assert get_k_factor(MatchContext(tournament="Friendly")) == 10
    assert get_k_factor(MatchContext(importance="friendly")) == 10
    assert get_k_factor(MatchContext(tournament="FIFA World Cup")) == 50


def test_get_k_factor_does_not_change_with_tournament_stage():
    assert get_k_factor(
        MatchContext(tournament="FIFA World Cup", importance="round_of_16")
    ) == 50
    assert get_k_factor(
        MatchContext(tournament="FIFA World Cup", importance="quarter_final")
    ) == 50
    assert get_k_factor(
        MatchContext(tournament="UEFA Nations League", importance="final")
    ) == 15


def test_tournament_configs_define_only_one_k_factor_each():
    tournaments = load_tournament_k_factors()

    assert all(
        [key for key in tournament if key.endswith("_k")] == ["default_k"]
        for tournament in tournaments.values()
    )


def test_margin_of_victory_factor_is_neutral_for_draws_and_capped():
    assert margin_of_victory_factor(0) == 1.0
    assert margin_of_victory_factor(1) == 1.0
    assert margin_of_victory_factor(10) == 2.0


def test_update_rating_still_accepts_old_arguments():
    updated = update_rating(
        rating=1500,
        opponent_rating=1500,
        actual_score=1.0,
        k_factor=20,
    )

    assert updated == 1510


def test_update_rating_uses_context_when_k_factor_is_not_provided():
    updated = update_rating(
        rating=1500,
        opponent_rating=1500,
        actual_score=1.0,
        context=MatchContext(tournament="Friendly"),
    )

    assert updated == 1505


def test_update_rating_applies_margin_of_victory_factor():
    one_goal_win = update_rating(
        rating=1500,
        opponent_rating=1500,
        actual_score=1.0,
        k_factor=20,
        goal_diff=1,
    )
    four_goal_win = update_rating(
        rating=1500,
        opponent_rating=1500,
        actual_score=1.0,
        k_factor=20,
        goal_diff=4,
    )

    assert four_goal_win > one_goal_win
