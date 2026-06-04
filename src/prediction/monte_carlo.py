from __future__ import annotations

import random
from collections import defaultdict

from src.prediction.tournament import simulate_tournament_once
from src.prediction.team_strength import TeamStrengthRating


def run_monte_carlo(
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]],
    third_place_combinations: dict[str, dict[str, str]] | None = None,
    simulations: int = 1000,
    seed: int | None = None,
    return_sample_outcome: bool = False,
    return_outcomes: bool = False,
    team_strength_ratings: dict[str, TeamStrengthRating] | None = None,
) -> dict:
    """Run repeated tournament simulations and aggregate advancement probabilities."""

    if simulations <= 0:
        raise ValueError("simulations must be greater than 0")
    if not groups:
        raise ValueError("groups must not be empty")
    if not ratings:
        raise ValueError("ratings must not be empty")

    rng = random.Random(seed)
    teams = [team for group_teams in groups.values() for team in group_teams]
    counts = {
        team: defaultdict(int)
        for team in teams
    }

    sample_outcome = None
    outcomes = []
    for _ in range(simulations):
        outcome = simulate_tournament_once(
            groups=groups,
            ratings=ratings,
            knockout_matches=knockout_matches,
            third_place_combinations=third_place_combinations,
            rng=rng,
            team_strength_ratings=team_strength_ratings,
        )
        if sample_outcome is None:
            sample_outcome = outcome
        if return_outcomes:
            outcomes.append(outcome)

        if outcome.champion is not None:
            counts[outcome.champion]["champion"] += 1
        if outcome.runner_up is not None:
            counts[outcome.runner_up]["runner_up"] += 1
        for team in outcome.semifinalists:
            counts[team]["semifinal"] += 1

    probabilities = {
        team: {
            "champion": counts[team]["champion"] / simulations,
            "runner_up": counts[team]["runner_up"] / simulations,
            "semifinal": counts[team]["semifinal"] / simulations,
        }
        for team in teams
    }

    if return_sample_outcome:
        return probabilities, sample_outcome

    if return_outcomes:
        return probabilities, outcomes

    return probabilities
