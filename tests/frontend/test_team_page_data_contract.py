import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREDICTIONS_DIR = PROJECT_ROOT / "outputs/predictions"


def load_json(filename: str):
    with (PREDICTIONS_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def stage_reached(team: str, representative: dict) -> str:
    stage_order = {
        "round_of_32": 1,
        "round_of_16": 2,
        "quarter_final": 3,
        "semi_final": 4,
        "third_place_playoff": 4,
        "final": 5,
    }
    labels = {
        "round_of_32": "Round of 32",
        "round_of_16": "Round of 16",
        "quarter_final": "Quarter-final",
        "semi_final": "Semi-final",
        "third_place_playoff": "Semi-final",
        "final": "Final",
    }
    matches = [
        match
        for match in representative["bracket"]
        if team in (match["home_team"], match["away_team"])
    ]
    if representative["champion"] == team:
        return "Champion"
    if not matches:
        return "Group Stage"

    furthest_round = max(matches, key=lambda match: stage_order[match["round"]])["round"]
    return labels[furthest_round]


def test_team_page_sources_are_complete_and_separated():
    metrics = load_json("world_cup_team_metrics.json")["teams"]
    probabilities = load_json("world_cup_probabilities.json")
    aggregate_groups = load_json("group_results.json")["groups"]
    representative = load_json("representative_tournament.json")["representative_tournament"]

    metric_teams = {row["team"] for row in metrics}
    probability_teams = {row["team"] for row in probabilities}
    aggregate_teams = {
        row["team"] for standings in aggregate_groups.values() for row in standings
    }
    representative_teams = {
        row["team"] for standings in representative["groups"].values() for row in standings
    }

    assert metric_teams == probability_teams == aggregate_teams == representative_teams

    result_fields = {
        "position",
        "points",
        "goals_for",
        "goals_against",
        "goal_difference",
        "qualified",
        "stage_reached",
    }
    assert all(result_fields.isdisjoint(row) for row in metrics)


def test_team_page_representative_summary_matches_groups_and_bracket():
    representative = load_json("representative_tournament.json")["representative_tournament"]
    qualified = set(representative["qualified"]["round_of_32"])
    group_matches = [match for match in representative["results"] if match["stage"] == "group"]

    for group, standings in representative["groups"].items():
        for standing in standings:
            team = standing["team"]
            matches = [
                match
                for match in group_matches
                if match["group"] == group
                and team in (match["home_team"], match["away_team"])
            ]
            goals_for = sum(
                match["predicted_home_goals"]
                if match["home_team"] == team
                else match["predicted_away_goals"]
                for match in matches
            )
            goals_against = sum(
                match["predicted_away_goals"]
                if match["home_team"] == team
                else match["predicted_home_goals"]
                for match in matches
            )
            points = sum(
                3
                if (
                    match["predicted_home_goals"] > match["predicted_away_goals"]
                    and match["home_team"] == team
                )
                or (
                    match["predicted_away_goals"] > match["predicted_home_goals"]
                    and match["away_team"] == team
                )
                else 1
                if match["predicted_home_goals"] == match["predicted_away_goals"]
                else 0
                for match in matches
            )
            bracket_matches = [
                match
                for match in representative["bracket"]
                if team in (match["home_team"], match["away_team"])
            ]

            assert standing["played"] == len(matches) == 3
            assert standing["points"] == points
            assert standing["goals_for"] == goals_for
            assert standing["goals_against"] == goals_against
            assert standing["goal_difference"] == goals_for - goals_against
            assert (team in qualified) == bool(bracket_matches)
            assert standing["position"] == standings.index(standing) + 1
            assert stage_reached(team, representative) in {
                "Group Stage",
                "Round of 32",
                "Round of 16",
                "Quarter-final",
                "Semi-final",
                "Final",
                "Champion",
            }
