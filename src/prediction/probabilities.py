from __future__ import annotations

import math

from src.elo.expected import expected_score


def draw_probability_from_elo_diff(elo_diff: float, base_draw_probability: float = 0.26, decay: float = 0.0008, min_draw_probability: float = 0.08) -> float:
    """
    Estimates draw probability from absolute Elo difference.

    Draw probability is highest when teams are evenly matched and decreases
    as the Elo gap grows.
    """
    draw_prob = base_draw_probability * math.exp(-decay * abs(elo_diff))
    return max(min_draw_probability, draw_prob)


def elo_win_draw_loss_probs(elo_a: float, elo_b: float, base_draw_probability: float = 0.26) -> tuple[float, float, float]:
    """
    Converts two Elo ratings into win/draw/loss probabilities for team A.

    Returns:
        (prob_a_win, prob_draw, prob_b_win)
    """
    expected_a = expected_score(elo_a, elo_b)
    draw_prob = draw_probability_from_elo_diff(
        elo_diff=elo_a - elo_b,
        base_draw_probability=base_draw_probability,
    )

    decisive_prob = 1.0 - draw_prob

    prob_a_win = decisive_prob * expected_a
    prob_b_win = decisive_prob * (1.0 - expected_a)

    return prob_a_win, draw_prob, prob_b_win