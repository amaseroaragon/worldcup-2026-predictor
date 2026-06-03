import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.elo.config import K_FACTOR


TOURNAMENT_K_FACTORS_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "external" / "tournament_k_factors.json"
)


@dataclass(frozen=True)
class MatchContext:
    """
    Context that can influence an Elo update.
    """

    tournament: str | None = None
    importance: str | None = None


@lru_cache(maxsize=1)
def load_tournament_k_factors(path: Path = TOURNAMENT_K_FACTORS_PATH) -> dict:
    """Load tournament-specific Elo K factors from JSON."""

    with path.open(encoding="utf-8") as file:
        return json.load(file)["tournaments"]


def _find_tournament_config(tournament_name: str) -> dict | None:
    tournaments = load_tournament_k_factors()
    if tournament_name in tournaments:
        return tournaments[tournament_name]

    normalised_name = tournament_name.strip().lower()
    for name, config in tournaments.items():
        if name.strip().lower() == normalised_name:
            return config

    return None


def get_k_factor(context: MatchContext | None = None) -> float:
    """
    Return the Elo K factor for a match context.

    With no context, this preserves the historical fixed K behavior.
    """

    if context is None:
        return K_FACTOR

    tournament_name = context.tournament or context.importance
    if tournament_name is None:
        return K_FACTOR

    tournament = _find_tournament_config(tournament_name)
    if tournament is None:
        return K_FACTOR

    return tournament["default_k"]
