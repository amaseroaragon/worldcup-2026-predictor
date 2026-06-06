from __future__ import annotations

from dataclasses import dataclass

from src.prediction.settings import MODEL_WEIGHTS, SIMULATION_SETTINGS


@dataclass(frozen=True)
class ModelVariant:
    """Declarative feature switches for backtesting model variants."""

    name: str
    use_attack_rating: bool
    use_defense_rating: bool
    use_recent_form: bool
    use_squad_strength: bool
    use_dynamic_elo_group_stage: bool
    use_dynamic_elo_knockout: bool


MODEL_VARIANTS: tuple[ModelVariant, ...] = (
    ModelVariant(
        name="EloOnly",
        use_attack_rating=False,
        use_defense_rating=False,
        use_recent_form=False,
        use_squad_strength=False,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="EloAttackDefense",
        use_attack_rating=True,
        use_defense_rating=True,
        use_recent_form=False,
        use_squad_strength=False,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="EloRecentForm",
        use_attack_rating=False,
        use_defense_rating=False,
        use_recent_form=True,
        use_squad_strength=False,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="EloSquadStrength",
        use_attack_rating=False,
        use_defense_rating=False,
        use_recent_form=False,
        use_squad_strength=True,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="EloAttackDefenseRecentForm",
        use_attack_rating=True,
        use_defense_rating=True,
        use_recent_form=True,
        use_squad_strength=False,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="EloAttackDefenseSquad",
        use_attack_rating=True,
        use_defense_rating=True,
        use_recent_form=False,
        use_squad_strength=True,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="FullModel",
        use_attack_rating=True,
        use_defense_rating=True,
        use_recent_form=MODEL_WEIGHTS.use_recent_form,
        use_squad_strength=MODEL_WEIGHTS.use_squad_strength,
        use_dynamic_elo_group_stage=SIMULATION_SETTINGS.use_dynamic_elo_group_stage,
        use_dynamic_elo_knockout=SIMULATION_SETTINGS.use_dynamic_elo_knockout,
    ),
    ModelVariant(
        name="FullNoDynamicElo",
        use_attack_rating=True,
        use_defense_rating=True,
        use_recent_form=MODEL_WEIGHTS.use_recent_form,
        use_squad_strength=MODEL_WEIGHTS.use_squad_strength,
        use_dynamic_elo_group_stage=False,
        use_dynamic_elo_knockout=False,
    ),
    ModelVariant(
        name="EloOnlyDynamic",
        use_attack_rating=False,
        use_defense_rating=False,
        use_recent_form=False,
        use_squad_strength=False,
        use_dynamic_elo_group_stage=SIMULATION_SETTINGS.use_dynamic_elo_group_stage,
        use_dynamic_elo_knockout=SIMULATION_SETTINGS.use_dynamic_elo_knockout,
    ),
)


MODEL_VARIANTS_BY_NAME = {variant.name: variant for variant in MODEL_VARIANTS}


def get_model_variant(name: str) -> ModelVariant:
    """Return a configured model variant by name."""

    try:
        return MODEL_VARIANTS_BY_NAME[name]
    except KeyError as exc:
        raise ValueError(f"Unknown model variant: {name}") from exc

