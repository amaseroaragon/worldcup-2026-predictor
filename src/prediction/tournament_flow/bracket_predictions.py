from __future__ import annotations

import hashlib
from collections import defaultdict

from src.prediction.core.match import _expected_goals_feature_kwargs
from src.prediction.tournament_flow.fixtures import build_group_stage_fixtures
from src.prediction.tournament_flow.knockout import (
    build_knockout_fixtures,
    build_third_place_placeholder_resolution,
    rank_third_place_teams,
    resolve_knockout_fixture,
)
from src.prediction.core.models import GroupOutcome, MatchPrediction, MatchResult, TournamentOutcome
from src.prediction.core.poisson import expected_goals_from_elo, score_matrix
from src.prediction.core.probabilities import elo_win_draw_loss_probs
from src.prediction.tournament_flow.prediction_summary import (
    average_goals,
    prediction_to_match_result,
    result_probabilities,
    select_representative_score,
)
from src.prediction.metrics.recent_form import RecentFormRating
from src.prediction.metrics.squad_strength import SquadStrengthRating
from src.prediction.core.standings import build_group_standings
from src.prediction.metrics.team_strength import TeamStrengthRating
from src.prediction.settings import DEFAULT_CLI_SEED


def build_predicted_bracket_predictions(
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]],
    third_place_combinations: dict[str, dict[str, str]] | None = None,
    team_strength_ratings: dict[str, TeamStrengthRating] | None = None,
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    group_matches: list[dict[str, str | int]] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
    representative_score_seed: int | str = DEFAULT_CLI_SEED,
) -> list[MatchPrediction]:
    """Build one frontend-ready predicted bracket from aggregate simulations."""

    if not outcomes:
        raise ValueError("outcomes must not be empty")

    simulations_count = len(outcomes)
    group_predictions = _build_group_stage_predictions(
        outcomes,
        groups,
        ratings,
        simulations_count,
        group_matches,
        team_strength_ratings,
        recent_form_ratings,
        squad_strength_ratings,
        representative_score_seed,
    )
    group_outcomes = build_representative_group_outcomes(group_predictions)
    knockout_predictions = _build_knockout_stage_predictions(
        outcomes,
        group_outcomes,
        ratings,
        knockout_matches,
        third_place_combinations,
        simulations_count,
        team_strength_ratings,
        recent_form_ratings,
        squad_strength_ratings,
        representative_score_seed,
    )

    return [*group_predictions, *knockout_predictions]


def _build_group_stage_predictions(
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    simulations_count: int,
    group_matches: list[dict[str, str | int]] | None,
    team_strength_ratings: dict[str, TeamStrengthRating] | None,
    recent_form_ratings: dict[str, RecentFormRating] | None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None,
    representative_score_seed: int | str,
) -> list[MatchPrediction]:
    results_by_match_id = _results_by_match_id(outcomes)
    predictions = []

    for fixture in build_group_stage_fixtures(groups, group_matches):
        results = results_by_match_id[fixture.match_id]
        predictions.append(
            _prediction_from_results(
                match_id=fixture.match_id,
                stage="group",
                group=fixture.group,
                round_name=None,
                home_team=fixture.team_a,
                away_team=fixture.team_b,
                results=results,
                ratings=ratings,
                simulations_count=simulations_count,
                appearance_count=len(results),
                source="aggregated_monte_carlo",
                team_strength_ratings=team_strength_ratings,
                recent_form_ratings=recent_form_ratings,
                squad_strength_ratings=squad_strength_ratings,
                representative_score_seed=representative_score_seed,
            )
        )

    return predictions


def build_representative_group_outcomes(
    group_predictions: list[MatchPrediction],
) -> dict[str, GroupOutcome]:
    """Build representative standings solely from displayed group scores."""
    results_by_group: dict[str, list[MatchResult]] = defaultdict(list)

    for prediction in group_predictions:
        if prediction.group is None:
            raise ValueError(f"Group prediction {prediction.match_id} is missing a group")

        is_draw = prediction.predicted_home_goals == prediction.predicted_away_goals
        winner = None if is_draw else prediction.predicted_winner
        results_by_group[prediction.group].append(
            MatchResult(
                team_a=prediction.home_team,
                team_b=prediction.away_team,
                goals_a=prediction.predicted_home_goals,
                goals_b=prediction.predicted_away_goals,
                winner=winner,
                is_draw=is_draw,
                decided_by="draw" if is_draw else "regular_time",
                match_id=prediction.match_id,
            )
        )

    group_outcomes = {}
    for group, results in results_by_group.items():
        standings = build_group_standings(results)
        group_outcomes[group] = GroupOutcome(
            group=group,
            standings=standings,
            winner=standings[0].team,
            runner_up=standings[1].team,
            third_place=standings[2].team if len(standings) > 2 else None,
            match_results=results,
        )

    return group_outcomes


def _build_knockout_stage_predictions(
    outcomes: list[TournamentOutcome],
    group_outcomes: dict[str, GroupOutcome],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]],
    third_place_combinations: dict[str, dict[str, str]] | None,
    simulations_count: int,
    team_strength_ratings: dict[str, TeamStrengthRating] | None,
    recent_form_ratings: dict[str, RecentFormRating] | None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None,
    representative_score_seed: int | str,
) -> list[MatchPrediction]:
    matchup_results = _knockout_results_by_matchup(outcomes)
    knockout_rounds = {
        match["match_id"]: match["round"]
        for match in knockout_matches
    }
    knockout_fixtures = build_knockout_fixtures(knockout_matches)
    match_results_by_id: dict[str, MatchResult] = {}
    predictions = []
    used_third_place_groups: set[str] = set()
    third_place_rankings = rank_third_place_teams(group_outcomes)
    third_place_placeholder_resolution = (
        build_third_place_placeholder_resolution(third_place_rankings, third_place_combinations)
        if third_place_combinations is not None
        else None
    )

    for fixture in knockout_fixtures:
        resolved_fixture = resolve_knockout_fixture(
            fixture=fixture,
            group_outcomes=group_outcomes,
            match_results=match_results_by_id,
            third_place_rankings=third_place_rankings,
            used_third_place_groups=used_third_place_groups,
            third_place_placeholder_resolution=third_place_placeholder_resolution,
        )
        key = (resolved_fixture.match_id, resolved_fixture.team_a, resolved_fixture.team_b)
        results = matchup_results.get(key, [])
        if results:
            prediction = _prediction_from_results(
                match_id=resolved_fixture.match_id,
                stage=resolved_fixture.stage,
                group=None,
                round_name=knockout_rounds.get(resolved_fixture.match_id, resolved_fixture.stage),
                home_team=resolved_fixture.team_a,
                away_team=resolved_fixture.team_b,
                results=results,
                ratings=ratings,
                simulations_count=simulations_count,
                appearance_count=len(results),
                source="aggregated_monte_carlo",
                knockout=True,
                team_strength_ratings=team_strength_ratings,
                recent_form_ratings=recent_form_ratings,
                squad_strength_ratings=squad_strength_ratings,
                representative_score_seed=representative_score_seed,
            )
        else:
            prediction = _prediction_from_direct_model(
                match_id=resolved_fixture.match_id,
                stage=resolved_fixture.stage,
                round_name=knockout_rounds.get(resolved_fixture.match_id, resolved_fixture.stage),
                home_team=resolved_fixture.team_a,
                away_team=resolved_fixture.team_b,
                ratings=ratings,
                simulations_count=simulations_count,
                team_strength_ratings=team_strength_ratings,
                recent_form_ratings=recent_form_ratings,
                squad_strength_ratings=squad_strength_ratings,
                representative_score_seed=representative_score_seed,
            )

        predictions.append(prediction)
        match_results_by_id[prediction.match_id] = prediction_to_match_result(prediction)

    return predictions


def _prediction_from_results(
    match_id: str,
    stage: str,
    group: str | None,
    round_name: str | None,
    home_team: str,
    away_team: str,
    results: list[MatchResult],
    ratings: dict[str, float],
    simulations_count: int,
    appearance_count: int,
    source: str,
    knockout: bool = False,
    team_strength_ratings: dict[str, TeamStrengthRating] | None = None,
    recent_form_ratings: dict[str, RecentFormRating] | None = None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None = None,
    representative_score_seed: int | str = DEFAULT_CLI_SEED,
) -> MatchPrediction:
    if not results:
        raise ValueError(f"No simulated results found for match {match_id}")

    home_win_probability, draw_probability, away_win_probability = result_probabilities(
        results,
        home_team,
        away_team,
        knockout=knockout,
    )
    expected_home_goals, expected_away_goals = _expected_goals_for_match(
        home_team,
        away_team,
        ratings,
        team_strength_ratings,
        recent_form_ratings,
        squad_strength_ratings,
    )
    predicted_home_goals, predicted_away_goals = select_representative_score(
        score_matrix(expected_home_goals, expected_away_goals),
        home_win_probability,
        draw_probability,
        away_win_probability,
        seed=_match_seed(representative_score_seed, match_id),
    )
    predicted_winner, advanced_by = _winner_from_representative_score(
        home_team,
        away_team,
        predicted_home_goals,
        predicted_away_goals,
        home_win_probability,
        away_win_probability,
        knockout,
    )

    return MatchPrediction(
        match_id=match_id,
        stage=stage,
        group=group,
        round=round_name,
        home_team=home_team,
        away_team=away_team,
        predicted_home_goals=predicted_home_goals,
        predicted_away_goals=predicted_away_goals,
        predicted_winner=predicted_winner,
        advanced_by=advanced_by,
        home_win_probability=home_win_probability,
        draw_probability=draw_probability,
        away_win_probability=away_win_probability,
        simulations_count=simulations_count,
        appearance_count=appearance_count,
        appearance_probability=appearance_count / simulations_count,
        average_home_goals=average_goals(results, home_team),
        average_away_goals=average_goals(results, away_team),
        most_common_score=f"{predicted_home_goals}-{predicted_away_goals}",
        source=source,
    )


def _prediction_from_direct_model(
    match_id: str,
    stage: str,
    round_name: str,
    home_team: str,
    away_team: str,
    ratings: dict[str, float],
    simulations_count: int,
    team_strength_ratings: dict[str, TeamStrengthRating] | None,
    recent_form_ratings: dict[str, RecentFormRating] | None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None,
    representative_score_seed: int | str,
) -> MatchPrediction:
    home_elo = ratings[home_team]
    away_elo = ratings[away_team]
    home_win_probability, draw_probability, away_win_probability = elo_win_draw_loss_probs(
        home_elo,
        away_elo,
    )
    expected_home_goals, expected_away_goals = _expected_goals_for_match(
        home_team,
        away_team,
        ratings,
        team_strength_ratings,
        recent_form_ratings,
        squad_strength_ratings,
    )
    predicted_home_goals, predicted_away_goals = select_representative_score(
        score_matrix(expected_home_goals, expected_away_goals),
        home_win_probability,
        draw_probability,
        away_win_probability,
        seed=_match_seed(representative_score_seed, match_id),
    )
    predicted_winner, advanced_by = _winner_from_representative_score(
        home_team,
        away_team,
        predicted_home_goals,
        predicted_away_goals,
        home_win_probability,
        away_win_probability,
        knockout=True,
    )

    return MatchPrediction(
        match_id=match_id,
        stage=stage,
        group=None,
        round=round_name,
        home_team=home_team,
        away_team=away_team,
        predicted_home_goals=predicted_home_goals,
        predicted_away_goals=predicted_away_goals,
        predicted_winner=predicted_winner,
        advanced_by=advanced_by,
        home_win_probability=home_win_probability,
        draw_probability=draw_probability,
        away_win_probability=away_win_probability,
        simulations_count=simulations_count,
        appearance_count=0,
        appearance_probability=0.0,
        average_home_goals=round(expected_home_goals, 4),
        average_away_goals=round(expected_away_goals, 4),
        most_common_score=f"{predicted_home_goals}-{predicted_away_goals}",
        source="direct_model_fallback",
    )


def _expected_goals_for_match(
    home_team: str,
    away_team: str,
    ratings: dict[str, float],
    team_strength_ratings: dict[str, TeamStrengthRating] | None,
    recent_form_ratings: dict[str, RecentFormRating] | None,
    squad_strength_ratings: dict[str, SquadStrengthRating] | None,
) -> tuple[float, float]:
    return expected_goals_from_elo(
        ratings[home_team],
        ratings[away_team],
        **_expected_goals_feature_kwargs(
            team_a=home_team,
            team_b=away_team,
            team_strength_ratings=team_strength_ratings,
            recent_form_ratings=recent_form_ratings,
            squad_strength_ratings=squad_strength_ratings,
        ),
    )


def _match_seed(base_seed: int | str, match_id: str) -> int:
    digest = hashlib.sha256(f"{base_seed}:{match_id}".encode()).digest()
    return int.from_bytes(digest[:8], byteorder="big")


def _winner_from_representative_score(
    home_team: str,
    away_team: str,
    home_goals: int,
    away_goals: int,
    home_win_probability: float,
    away_win_probability: float,
    knockout: bool,
) -> tuple[str | None, str | None]:
    if home_goals > away_goals:
        return home_team, "normal_time_win" if knockout else None
    if away_goals > home_goals:
        return away_team, "normal_time_win" if knockout else None
    if not knockout:
        return None, None

    winner = home_team if home_win_probability >= away_win_probability else away_team
    return winner, "higher_win_probability_after_draw"


def _results_by_match_id(outcomes: list[TournamentOutcome]) -> dict[str, list[MatchResult]]:
    results_by_match_id: dict[str, list[MatchResult]] = defaultdict(list)
    for outcome in outcomes:
        for result in outcome.match_results:
            if result.match_id is not None:
                results_by_match_id[result.match_id].append(result)
    return results_by_match_id


def _knockout_results_by_matchup(
    outcomes: list[TournamentOutcome],
) -> dict[tuple[str, str, str], list[MatchResult]]:
    results_by_matchup: dict[tuple[str, str, str], list[MatchResult]] = defaultdict(list)
    for outcome in outcomes:
        for result in outcome.match_results:
            if result.match_id is None or result.match_id.startswith("group_"):
                continue
            key = (result.match_id, result.team_a, result.team_b)
            results_by_matchup[key].append(result)
    return results_by_matchup
