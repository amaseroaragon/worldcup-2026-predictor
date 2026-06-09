from __future__ import annotations

from dataclasses import asdict

from src.prediction.core.models import MatchPrediction
from src.prediction.tournament_flow.bracket_predictions import (
    build_representative_group_outcomes,
)
from src.prediction.tournament_flow.knockout import rank_third_place_teams


ROUND_TEAM_COUNTS = {
    "round_of_32": 32,
    "round_of_16": 16,
    "quarter_final": 8,
    "semi_final": 4,
    "final": 2,
}


def build_representative_tournament(
    predictions: list[MatchPrediction],
    knockout_matches: list[dict[str, str]],
    qualification_probabilities: dict[str, float] | None = None,
) -> dict:
    """Build one coherent tournament scenario from displayed match predictions."""
    group_predictions = [prediction for prediction in predictions if prediction.stage == "group"]
    bracket_predictions = [prediction for prediction in predictions if prediction.stage != "group"]
    group_outcomes = build_representative_group_outcomes(group_predictions)
    third_place_rankings = rank_third_place_teams(group_outcomes)
    best_third_teams = [row.team for _group, row in third_place_rankings[:8]]
    group_winners = [outcome.winner for outcome in group_outcomes.values()]
    runners_up = [outcome.runner_up for outcome in group_outcomes.values()]
    round_of_32 = [*group_winners, *runners_up, *best_third_teams]
    final = next((prediction for prediction in bracket_predictions if prediction.round == "final"), None)

    groups = {
        group: [
            {
                "position": position,
                **asdict(row),
                "goal_difference": row.goal_difference,
                "qualification_probability": (
                    qualification_probabilities or {}
                ).get(row.team),
            }
            for position, row in enumerate(outcome.standings, start=1)
        ]
        for group, outcome in sorted(group_outcomes.items())
    }
    best_third_places = [
        {
            "rank": rank,
            "group": group,
            **asdict(row),
            "goal_difference": row.goal_difference,
            "qualified": rank <= 8,
        }
        for rank, (group, row) in enumerate(third_place_rankings, start=1)
    ]
    resolved_bracket = _build_resolved_bracket(
        bracket_predictions,
        knockout_matches,
        group_outcomes,
    )
    payload = {
        "results": [asdict(prediction) for prediction in predictions],
        "groups": groups,
        "best_third_places": best_third_places,
        "qualified": {
            "group_winners": group_winners,
            "runners_up": runners_up,
            "best_third_places": best_third_teams,
            "round_of_32": round_of_32,
        },
        "bracket": resolved_bracket,
        "champion": final.predicted_winner if final else None,
    }
    validate_representative_tournament(payload, knockout_matches)
    return payload


def _build_resolved_bracket(
    bracket_predictions: list[MatchPrediction],
    knockout_matches: list[dict[str, str]],
    group_outcomes: dict,
) -> list[dict]:
    configs = {match["match_id"]: match for match in knockout_matches}
    team_group_positions = {
        row.team: (group, position)
        for group, outcome in group_outcomes.items()
        for position, row in enumerate(outcome.standings, start=1)
    }
    resolved = []
    for prediction in bracket_predictions:
        config = configs[prediction.match_id]
        home_source = _resolved_source(
            config["home"],
            prediction.home_team,
            team_group_positions,
        )
        away_source = _resolved_source(
            config["away"],
            prediction.away_team,
            team_group_positions,
        )
        source_match_ids = [
            source["match_id"]
            for source in (home_source, away_source)
            if source["match_id"] is not None
        ]
        resolved.append(
            {
                **asdict(prediction),
                "home_score": prediction.predicted_home_goals,
                "away_score": prediction.predicted_away_goals,
                "predicted_score": (
                    f"{prediction.predicted_home_goals}-{prediction.predicted_away_goals}"
                ),
                "winner": prediction.predicted_winner,
                "source": {
                    "home": home_source["label"],
                    "away": away_source["label"],
                },
                "source_match_ids": source_match_ids,
            }
        )
    return resolved


def _resolved_source(
    configured_source: str,
    team: str,
    team_group_positions: dict[str, tuple[str, int]],
) -> dict[str, str | None]:
    if configured_source.startswith("RU"):
        match_id = f"M{configured_source.removeprefix('RU')}"
        return {"label": f"Loser of {match_id}", "match_id": match_id}
    if configured_source.startswith("W"):
        match_id = f"M{configured_source.removeprefix('W')}"
        return {"label": f"Winner of {match_id}", "match_id": match_id}

    group, position = team_group_positions[team]
    labels = {1: "winner", 2: "runner-up", 3: "third place"}
    return {
        "label": f"Group {group} {labels[position]}",
        "match_id": None,
    }


def validate_representative_tournament(
    representative_tournament: dict,
    knockout_matches: list[dict[str, str]],
) -> None:
    """Validate standings, qualifiers, and bracket against the same displayed results."""
    predictions = [
        MatchPrediction(**record)
        for record in representative_tournament["results"]
    ]
    group_predictions = [prediction for prediction in predictions if prediction.stage == "group"]
    expected_outcomes = build_representative_group_outcomes(group_predictions)

    for group, outcome in expected_outcomes.items():
        exported = representative_tournament["groups"][group]
        exported_teams = [row["team"] for row in exported]
        expected_teams = [row.team for row in outcome.standings]
        if exported_teams != expected_teams:
            raise ValueError(f"Representative standings are inconsistent for group {group}")
        for exported_row, expected_row in zip(exported, outcome.standings):
            for field in ("played", "points", "goals_for", "goals_against", "wins", "draws", "losses"):
                if exported_row[field] != getattr(expected_row, field):
                    raise ValueError(
                        f"Representative standings field {field} is inconsistent for "
                        f"{expected_row.team}"
                    )
            if exported_row["goal_difference"] != expected_row.goal_difference:
                raise ValueError(
                    f"Representative standings field goal_difference is inconsistent for "
                    f"{expected_row.team}"
                )

    rankings = rank_third_place_teams(expected_outcomes)
    expected_qualified = {
        *(outcome.winner for outcome in expected_outcomes.values()),
        *(outcome.runner_up for outcome in expected_outcomes.values()),
        *(row.team for _group, row in rankings[:8]),
    }
    exported_qualified = set(representative_tournament["qualified"]["round_of_32"])
    if exported_qualified != expected_qualified or len(exported_qualified) != len(expected_qualified):
        raise ValueError("Representative qualifiers are inconsistent with standings")
    expected_group_winners = {outcome.winner for outcome in expected_outcomes.values()}
    expected_runners_up = {outcome.runner_up for outcome in expected_outcomes.values()}
    if set(representative_tournament["qualified"]["group_winners"]) != expected_group_winners:
        raise ValueError("Representative group winners are inconsistent with standings")
    if set(representative_tournament["qualified"]["runners_up"]) != expected_runners_up:
        raise ValueError("Representative runners-up are inconsistent with standings")
    expected_third_places = [
        (group, row.team, rank <= 8)
        for rank, (group, row) in enumerate(rankings, start=1)
    ]
    exported_third_places = [
        (row["group"], row["team"], row["qualified"])
        for row in representative_tournament["best_third_places"]
    ]
    if exported_third_places != expected_third_places:
        raise ValueError("Representative best third-place ranking is inconsistent")

    bracket_by_id = {
        match["match_id"]: match
        for match in representative_tournament["bracket"]
    }
    if set(bracket_by_id) != {match["match_id"] for match in knockout_matches}:
        raise ValueError("Representative bracket match IDs do not match configured bracket")
    for match in representative_tournament["bracket"]:
        if not match["home_team"] or not match["away_team"]:
            raise ValueError(f"Representative bracket match {match['match_id']} has an empty team")
        if match["winner"] not in {match["home_team"], match["away_team"]}:
            raise ValueError(
                f"Representative bracket winner is not a participant: {match['match_id']}"
            )
        if match["winner"] != match["predicted_winner"]:
            raise ValueError(f"Representative bracket winner alias is inconsistent: {match['match_id']}")
        if match["predicted_score"] != f"{match['home_score']}-{match['away_score']}":
            raise ValueError(f"Representative bracket score aliases are inconsistent: {match['match_id']}")

    for round_name, expected_team_count in ROUND_TEAM_COUNTS.items():
        round_matches = [
            match for match in representative_tournament["bracket"]
            if match["round"] == round_name
        ]
        round_teams = [
            team
            for match in round_matches
            for team in (match["home_team"], match["away_team"])
        ]
        if len(round_teams) != expected_team_count:
            raise ValueError(
                f"Representative {round_name} must contain {expected_team_count} teams"
            )
        if len(set(round_teams)) != expected_team_count:
            raise ValueError(f"A team appears twice in representative {round_name}")
    first_round_ids = [
        match["match_id"]
        for match in knockout_matches
        if match["round"] == "round_of_32"
    ]
    first_round_teams = {
        team
        for match_id in first_round_ids
        for team in (
            bracket_by_id[match_id]["home_team"],
            bracket_by_id[match_id]["away_team"],
        )
    }
    if first_round_teams != expected_qualified:
        raise ValueError("Representative bracket is inconsistent with qualifiers")

    for config in knockout_matches:
        match = bracket_by_id[config["match_id"]]
        expected_source_match_ids = [
            f"M{source.removeprefix('W')}"
            if source.startswith("W")
            else f"M{source.removeprefix('RU')}"
            for source in (config["home"], config["away"])
            if source.startswith(("W", "RU"))
        ]
        if match["source_match_ids"] != expected_source_match_ids:
            raise ValueError(
                f"Representative bracket sources are inconsistent: {match['match_id']}"
            )
        for side, source in (("home_team", config["home"]), ("away_team", config["away"])):
            source_key = "home" if side == "home_team" else "away"
            if len(source) == 2 and source[0] in {"1", "2"}:
                outcome = expected_outcomes[source[1]]
                expected_team = outcome.winner if source[0] == "1" else outcome.runner_up
                if match[side] != expected_team:
                    raise ValueError(
                        f"Representative bracket group path is inconsistent: {source}"
                    )
                expected_label = (
                    f"Group {source[1]} winner"
                    if source[0] == "1"
                    else f"Group {source[1]} runner-up"
                )
                if match["source"][source_key] != expected_label:
                    raise ValueError(
                        f"Representative bracket source label is inconsistent: {source}"
                    )
            elif source.startswith("3"):
                qualified_thirds = {
                    row.team: group
                    for group, row in rankings[:8]
                }
                if match[side] not in qualified_thirds:
                    raise ValueError(
                        f"Representative bracket third-place path is inconsistent: {source}"
                    )
                group = qualified_thirds[match[side]]
                if group not in set(source.removeprefix("3")):
                    raise ValueError(
                        f"Representative bracket third-place group is not allowed: {source}"
                    )
                if match["source"][source_key] != f"Group {group} third place":
                    raise ValueError(
                        f"Representative bracket source label is inconsistent: {source}"
                    )
            elif source.startswith("W"):
                source_match = bracket_by_id[f"M{source.removeprefix('W')}"]
                if match[side] != source_match["predicted_winner"]:
                    raise ValueError(f"Representative bracket winner path is inconsistent: {source}")
                if match["source"][source_key] != f"Winner of {source_match['match_id']}":
                    raise ValueError(
                        f"Representative bracket source label is inconsistent: {source}"
                    )
            elif source.startswith("RU"):
                source_match = bracket_by_id[f"M{source.removeprefix('RU')}"]
                loser = (
                    source_match["away_team"]
                    if source_match["predicted_winner"] == source_match["home_team"]
                    else source_match["home_team"]
                )
                if match[side] != loser:
                    raise ValueError(f"Representative bracket loser path is inconsistent: {source}")
                if match["source"][source_key] != f"Loser of {source_match['match_id']}":
                    raise ValueError(
                        f"Representative bracket source label is inconsistent: {source}"
                    )

    final = next(match for match in representative_tournament["bracket"] if match["round"] == "final")
    if representative_tournament["champion"] != final["predicted_winner"]:
        raise ValueError("Representative champion is inconsistent with final")
