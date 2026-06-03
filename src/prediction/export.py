from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.prediction.fixtures import build_group_stage_fixtures
from src.prediction.knockout import (
    build_knockout_fixtures,
    build_third_place_placeholder_resolution,
    rank_third_place_teams,
    resolve_knockout_fixture,
)
from src.prediction.models import GroupOutcome, MatchPrediction, MatchResult, TournamentOutcome
from src.prediction.poisson import expected_goals_from_elo
from src.prediction.probabilities import elo_win_draw_loss_probs
from src.prediction.standings import build_group_standings


PROBABILITY_COLUMNS = [
    "team",
    "champion_probability",
    "runner_up_probability",
    "semifinal_probability",
]
PROBABILITY_VALUE_COLUMNS = PROBABILITY_COLUMNS[1:]
DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH = Path(
    "outputs/predictions/tournament_predictions.json"
)


def probabilities_to_dataframe(probabilities: dict) -> pd.DataFrame:
    """Convert aggregate tournament probabilities into a sorted dataframe."""

    rows = [
        {
            "team": team,
            "champion_probability": values["champion"],
            "runner_up_probability": values["runner_up"],
            "semifinal_probability": values["semifinal"],
        }
        for team, values in probabilities.items()
    ]

    return (
        pd.DataFrame(rows, columns=PROBABILITY_COLUMNS)
        .sort_values("champion_probability", ascending=False)
        .reset_index(drop=True)
    )


def export_probabilities(probabilities: dict, output_path: str | Path) -> pd.DataFrame:
    """Write aggregate tournament probabilities to CSV."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = probabilities_to_dataframe(probabilities)
    df.to_csv(output_path, index=False)

    return df


def build_match_predictions(
    match_results: list[MatchResult],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]] | None = None,
) -> list[MatchPrediction]:
    """Build persistable match prediction records from simulated match results."""

    knockout_rounds = {
        match["match_id"]: match["round"]
        for match in knockout_matches or []
    }
    return [
        _build_match_prediction(result, ratings, knockout_rounds)
        for result in match_results
    ]


def build_predicted_bracket_predictions(
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    knockout_matches: list[dict[str, str]],
    third_place_combinations: dict[str, dict[str, str]] | None = None,
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
    )
    group_outcomes = _build_predicted_group_outcomes(group_predictions)
    knockout_predictions = _build_knockout_stage_predictions(
        outcomes,
        group_outcomes,
        ratings,
        knockout_matches,
        third_place_combinations,
        simulations_count,
    )

    return [*group_predictions, *knockout_predictions]


def export_match_predictions_json(
    predictions: list[MatchPrediction],
    output_path: str | Path = DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
    metadata: dict | None = None,
) -> dict:
    """Write match predictions to a JSON file."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [asdict(prediction) for prediction in predictions]
    payload = {
        "metadata": metadata or {},
        "matches": rows,
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    return payload


def validate_probability_output(df: pd.DataFrame) -> None:
    """Validate the exported probability dataframe contract."""

    missing_columns = set(PROBABILITY_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing probability output columns: {missing}")

    if df.empty:
        raise ValueError("Probability output is empty")

    null_counts = df[PROBABILITY_COLUMNS].isna().sum()
    invalid_nulls = null_counts[null_counts > 0]
    if not invalid_nulls.empty:
        raise ValueError(f"Probability output contains null values:\n{invalid_nulls}")

    for column in PROBABILITY_VALUE_COLUMNS:
        if not df[column].between(0, 1).all():
            raise ValueError(f"{column} must contain values between 0 and 1")

    champion_probability_sum = df["champion_probability"].sum()
    if abs(champion_probability_sum - 1.0) > 1e-9:
        raise ValueError("Champion probabilities must sum to 1")


def _build_match_prediction(
    result: MatchResult,
    ratings: dict[str, float],
    knockout_rounds: dict[str, str],
) -> MatchPrediction:
    missing_ratings = [
        team for team in (result.team_a, result.team_b) if team not in ratings
    ]
    if missing_ratings:
        missing = ", ".join(missing_ratings)
        raise ValueError(f"Missing Elo rating for: {missing}")

    home_elo = ratings[result.team_a]
    away_elo = ratings[result.team_b]
    home_win_probability, draw_probability, away_win_probability = elo_win_draw_loss_probs(
        home_elo,
        away_elo,
    )
    stage, group, round_name = _match_metadata(result.match_id, knockout_rounds)

    return MatchPrediction(
        match_id=result.match_id or "",
        stage=stage,
        group=group,
        round=round_name,
        home_team=result.team_a,
        away_team=result.team_b,
        predicted_home_goals=result.goals_a,
        predicted_away_goals=result.goals_b,
        predicted_winner=result.winner,
        home_win_probability=home_win_probability,
        draw_probability=draw_probability,
        away_win_probability=away_win_probability,
    )


def _build_group_stage_predictions(
    outcomes: list[TournamentOutcome],
    groups: dict[str, list[str]],
    ratings: dict[str, float],
    simulations_count: int,
) -> list[MatchPrediction]:
    results_by_match_id = _results_by_match_id(outcomes)
    predictions = []

    for fixture in build_group_stage_fixtures(groups):
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
            )
        )

    return predictions


def _build_predicted_group_outcomes(
    group_predictions: list[MatchPrediction],
) -> dict[str, GroupOutcome]:
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
            )

        predictions.append(prediction)
        match_results_by_id[prediction.match_id] = _prediction_to_match_result(prediction)

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
) -> MatchPrediction:
    if not results:
        raise ValueError(f"No simulated results found for match {match_id}")

    home_win_probability, draw_probability, away_win_probability = _result_probabilities(
        results,
        home_team,
        away_team,
        knockout=knockout,
    )
    predicted_winner = _predicted_winner(
        home_team,
        away_team,
        home_win_probability,
        draw_probability,
        away_win_probability,
        allow_draw=not knockout,
    )
    predicted_home_goals, predicted_away_goals = _most_common_score(
        results,
        predicted_winner,
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
        home_win_probability=home_win_probability,
        draw_probability=draw_probability,
        away_win_probability=away_win_probability,
        simulations_count=simulations_count,
        appearance_count=appearance_count,
        appearance_probability=appearance_count / simulations_count,
        average_home_goals=_average_goals(results, home_team),
        average_away_goals=_average_goals(results, away_team),
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
) -> MatchPrediction:
    home_elo = ratings[home_team]
    away_elo = ratings[away_team]
    home_win_probability, _draw_probability, away_win_probability = elo_win_draw_loss_probs(
        home_elo,
        away_elo,
    )
    decisive_probability = home_win_probability + away_win_probability
    home_win_probability = home_win_probability / decisive_probability
    away_win_probability = away_win_probability / decisive_probability
    expected_home_goals, expected_away_goals = expected_goals_from_elo(home_elo, away_elo)
    predicted_home_goals = round(expected_home_goals)
    predicted_away_goals = round(expected_away_goals)
    predicted_winner = home_team if home_win_probability >= away_win_probability else away_team

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
        home_win_probability=home_win_probability,
        draw_probability=0.0,
        away_win_probability=away_win_probability,
        simulations_count=simulations_count,
        appearance_count=0,
        appearance_probability=0.0,
        average_home_goals=round(expected_home_goals, 4),
        average_away_goals=round(expected_away_goals, 4),
        most_common_score=f"{predicted_home_goals}-{predicted_away_goals}",
        source="direct_model_fallback",
    )


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


def _result_probabilities(
    results: list[MatchResult],
    home_team: str,
    away_team: str,
    knockout: bool,
) -> tuple[float, float, float]:
    total = len(results)
    home_wins = sum(result.winner == home_team for result in results)
    away_wins = sum(result.winner == away_team for result in results)
    draws = 0 if knockout else sum(result.winner is None for result in results)

    return home_wins / total, draws / total, away_wins / total


def _most_common_score(
    results: list[MatchResult],
    predicted_winner: str | None,
) -> tuple[int, int]:
    matching_results = [
        result for result in results
        if result.winner == predicted_winner
    ]
    score_results = matching_results or results
    return Counter(
        (result.goals_a, result.goals_b)
        for result in score_results
    ).most_common(1)[0][0]


def _average_goals(results: list[MatchResult], team: str) -> float:
    goals = [
        result.goals_a if result.team_a == team else result.goals_b
        for result in results
    ]
    return round(sum(goals) / len(goals), 4)


def _predicted_winner(
    home_team: str,
    away_team: str,
    home_win_probability: float,
    draw_probability: float,
    away_win_probability: float,
    allow_draw: bool,
) -> str | None:
    if allow_draw and draw_probability >= max(home_win_probability, away_win_probability):
        return None
    if home_win_probability >= away_win_probability:
        return home_team
    return away_team


def _prediction_to_match_result(prediction: MatchPrediction) -> MatchResult:
    is_draw = prediction.predicted_home_goals == prediction.predicted_away_goals
    return MatchResult(
        team_a=prediction.home_team,
        team_b=prediction.away_team,
        goals_a=prediction.predicted_home_goals,
        goals_b=prediction.predicted_away_goals,
        winner=prediction.predicted_winner,
        is_draw=prediction.predicted_winner is None,
        decided_by="tiebreaker" if is_draw and prediction.predicted_winner else "regular_time",
        match_id=prediction.match_id,
    )


def _match_metadata(
    match_id: str | None,
    knockout_rounds: dict[str, str],
) -> tuple[str, str | None, str | None]:
    if match_id is None:
        return "unknown", None, None

    if match_id.startswith("group_"):
        parts = match_id.split("_")
        group = parts[1] if len(parts) >= 3 else None
        return "group", group, None

    round_name = knockout_rounds.get(match_id)
    if round_name is not None:
        return round_name, None, round_name

    return "knockout", None, None
