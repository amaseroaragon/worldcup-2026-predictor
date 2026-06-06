from src.backtesting.model_variants import MODEL_VARIANTS_BY_NAME
from src.prediction.settings import MODEL_WEIGHTS, SIMULATION_SETTINGS


def test_expected_model_variants_are_defined():
    assert set(MODEL_VARIANTS_BY_NAME) == {
        "EloOnly",
        "EloAttackDefense",
        "EloRecentForm",
        "EloSquadStrength",
        "EloAttackDefenseRecentForm",
        "EloAttackDefenseSquad",
        "FullModel",
        "FullNoDynamicElo",
        "EloOnlyDynamic",
    }


def test_elo_only_disables_extra_factors():
    variant = MODEL_VARIANTS_BY_NAME["EloOnly"]

    assert variant.use_attack_rating is False
    assert variant.use_defense_rating is False
    assert variant.use_recent_form is False
    assert variant.use_squad_strength is False
    assert variant.use_dynamic_elo_group_stage is False
    assert variant.use_dynamic_elo_knockout is False


def test_full_model_matches_current_model_switches():
    variant = MODEL_VARIANTS_BY_NAME["FullModel"]

    assert variant.use_attack_rating is True
    assert variant.use_defense_rating is True
    assert variant.use_recent_form == MODEL_WEIGHTS.use_recent_form
    assert variant.use_squad_strength == MODEL_WEIGHTS.use_squad_strength
    assert variant.use_dynamic_elo_group_stage == (
        SIMULATION_SETTINGS.use_dynamic_elo_group_stage
    )
    assert variant.use_dynamic_elo_knockout == SIMULATION_SETTINGS.use_dynamic_elo_knockout

