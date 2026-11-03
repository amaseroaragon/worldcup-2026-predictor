"""Exact model probabilities for a given pairing, using pre-tournament inputs.

A Monte Carlo run only produces probabilities for pairings it happens to
simulate. For a fixed pairing the simulation converges to this closed form,
built from the model's own pieces: expected goals, the Poisson score matrix
and the knockout tiebreaker. Ratings are the pre-tournament ones (no
in-tournament Elo updates), i.e. the model's view before kick-off.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.prediction.core.match import _expected_goals_feature_kwargs, knockout_tiebreaker_probability
from src.prediction.core.poisson import expected_goals_from_elo, score_matrix
from src.prediction.pipeline import PredictionInputs


@dataclass(frozen=True)
class MatchProbabilities:
    expected_goals_a: float
    expected_goals_b: float
    win_a: float
    draw: float
    win_b: float
    advance_a: float

    @property
    def advance_b(self) -> float:
        return 1 - self.advance_a


def match_probabilities(team_a: str, team_b: str, inputs: PredictionInputs) -> MatchProbabilities:
    """90-minute win/draw/loss and probability of advancing for team A against team B."""

    elo_a, elo_b = inputs.ratings[team_a], inputs.ratings[team_b]
    expected_a, expected_b = expected_goals_from_elo(
        elo_a,
        elo_b,
        **_expected_goals_feature_kwargs(
            team_a=team_a,
            team_b=team_b,
            team_strength_ratings=inputs.team_strength_ratings,
            recent_form_ratings=inputs.recent_form_ratings,
            squad_strength_ratings=inputs.squad_strength_ratings,
        ),
    )

    matrix = score_matrix(expected_a, expected_b)
    win_a = sum(p for i, row in enumerate(matrix) for j, p in enumerate(row) if i > j)
    draw = sum(row[i] for i, row in enumerate(matrix))
    win_b = sum(p for i, row in enumerate(matrix) for j, p in enumerate(row) if j > i)
    total = win_a + draw + win_b  # < 1 only by the truncation at max_goals
    win_a, draw, win_b = win_a / total, draw / total, win_b / total

    tiebreak_a = knockout_tiebreaker_probability(elo_a, elo_b, expected_a, expected_b)
    return MatchProbabilities(
        expected_goals_a=expected_a,
        expected_goals_b=expected_b,
        win_a=win_a,
        draw=draw,
        win_b=win_b,
        advance_a=win_a + draw * tiebreak_a,
    )
