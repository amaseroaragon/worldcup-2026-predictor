"""Compare the pre-tournament forecast with the real World Cup 2026 results.

Nothing here feeds back into the model: it only reads the published
prediction outputs and a file of actual results.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.evaluation.match_probabilities import MatchProbabilities

KNOCKOUT_STAGES: tuple[tuple[str, int], ...] = (
    ("round_of_32", 16),
    ("round_of_16", 8),
    ("quarter_final", 4),
    ("semi_final", 2),
    ("third_place_playoff", 1),
    ("final", 1),
)
GROUP_MATCHES = 72
STAGE_ORDER = {
    "group": 0,
    "round_of_32": 1,
    "round_of_16": 2,
    "quarter_final": 3,
    "semi_final": 4,
    "final": 5,
    "champion": 6,
}
ACTUAL_RESULT_FIELDS = (
    "match_number",
    "date",
    "stage",
    "group",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "shootout_winner",
    "winner",
)


@dataclass(frozen=True)
class ActualMatch:
    match_number: int
    date: str
    stage: str
    group: str | None
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    shootout_winner: str | None
    winner: str | None

    @property
    def outcome(self) -> str:
        if self.home_score > self.away_score:
            return "home"
        if self.home_score < self.away_score:
            return "away"
        return "draw"

    @property
    def loser(self) -> str | None:
        if self.winner is None:
            return None
        return self.away_team if self.winner == self.home_team else self.home_team


def _group_of(team: str, groups: Mapping[str, Sequence[str]]) -> str:
    for group, teams in groups.items():
        if team in teams:
            return group
    raise ValueError(f"Team {team!r} is not in any World Cup 2026 group")


def build_actual_matches(
    results: Iterable[Mapping[str, str]],
    shootouts: Iterable[Mapping[str, str]],
    groups: Mapping[str, Sequence[str]],
) -> list[ActualMatch]:
    """Turn raw international results rows into the 104 World Cup 2026 matches.

    Rows are ordered by date; the first 72 are the group stage and the rest
    follow the fixed knockout calendar. The structure is validated so a
    mislabelled row fails loudly instead of producing a wrong comparison.
    """

    rows = sorted(
        (
            row
            for row in results
            if row["tournament"] == "FIFA World Cup" and row["date"].startswith("2026-")
        ),
        key=lambda row: row["date"],
    )
    expected = GROUP_MATCHES + sum(count for _, count in KNOCKOUT_STAGES)
    if len(rows) != expected:
        raise ValueError(f"Expected {expected} World Cup 2026 matches, found {len(rows)}")

    shootout_winners = {
        (row["date"], row["home_team"], row["away_team"]): row["winner"] for row in shootouts
    }
    stages = ["group"] * GROUP_MATCHES + [
        stage for stage, count in KNOCKOUT_STAGES for _ in range(count)
    ]

    matches: list[ActualMatch] = []
    for index, (row, stage) in enumerate(zip(rows, stages, strict=True)):
        home, away = row["home_team"], row["away_team"]
        home_score, away_score = int(row["home_score"]), int(row["away_score"])
        shootout = shootout_winners.get((row["date"], home, away))
        group = None

        if stage == "group":
            group = _group_of(home, groups)
            if _group_of(away, groups) != group:
                raise ValueError(f"Match {index + 1} ({home} v {away}) is not a group fixture")
            winner = home if home_score > away_score else away if away_score > home_score else None
        else:
            if home_score != away_score:
                winner = home if home_score > away_score else away
            elif shootout in (home, away):
                winner = shootout
            else:
                raise ValueError(f"Knockout match {home} v {away} has no winner")

        matches.append(
            ActualMatch(
                match_number=index + 1,
                date=row["date"],
                stage=stage,
                group=group,
                home_team=home,
                away_team=away,
                home_score=home_score,
                away_score=away_score,
                shootout_winner=shootout,
                winner=winner,
            )
        )

    _validate_knockout_progression(matches)
    return matches


def _validate_knockout_progression(matches: Sequence[ActualMatch]) -> None:
    by_stage: dict[str, list[ActualMatch]] = {}
    for match in matches:
        by_stage.setdefault(match.stage, []).append(match)

    previous_winners: set[str] | None = None
    for stage in ("round_of_32", "round_of_16", "quarter_final", "semi_final", "final"):
        teams = {team for match in by_stage[stage] for team in (match.home_team, match.away_team)}
        if previous_winners is not None and teams != previous_winners:
            raise ValueError(f"{stage} teams do not match the winners of the previous round")
        previous_winners = {match.winner for match in by_stage[stage] if match.winner}

    semi_losers = {match.loser for match in by_stage["semi_final"]}
    third_place = by_stage["third_place_playoff"][0]
    if {third_place.home_team, third_place.away_team} != semi_losers:
        raise ValueError("Third-place playoff teams are not the semi-final losers")


def write_actual_matches(matches: Sequence[ActualMatch], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=ACTUAL_RESULT_FIELDS)
        writer.writeheader()
        for match in matches:
            writer.writerow({field: getattr(match, field) or "" for field in ACTUAL_RESULT_FIELDS} | {
                "match_number": match.match_number,
                "home_score": match.home_score,
                "away_score": match.away_score,
            })


def read_actual_matches(path: Path) -> list[ActualMatch]:
    with path.open(encoding="utf-8", newline="") as file:
        return [
            ActualMatch(
                match_number=int(row["match_number"]),
                date=row["date"],
                stage=row["stage"],
                group=row["group"] or None,
                home_team=row["home_team"],
                away_team=row["away_team"],
                home_score=int(row["home_score"]),
                away_score=int(row["away_score"]),
                shootout_winner=row["shootout_winner"] or None,
                winner=row["winner"] or None,
            )
            for row in csv.DictReader(file)
        ]


def actual_stage_reached(matches: Sequence[ActualMatch]) -> dict[str, str]:
    """Furthest stage each team reached ("group" ... "champion")."""

    reached: dict[str, str] = {}

    def promote(team: str, stage: str) -> None:
        if team not in reached or STAGE_ORDER[stage] > STAGE_ORDER[reached[team]]:
            reached[team] = stage

    for match in matches:
        stage = "semi_final" if match.stage == "third_place_playoff" else match.stage
        promote(match.home_team, stage)
        promote(match.away_team, stage)
        if match.stage == "final" and match.winner:
            promote(match.winner, "champion")
    return reached


def _brier_binary(pairs: Iterable[tuple[float, bool]]) -> float:
    values = [(probability - float(happened)) ** 2 for probability, happened in pairs]
    return sum(values) / len(values)


def _rank(values: Mapping[str, float], team: str) -> int:
    return 1 + sum(1 for value in values.values() if value > values[team])


def evaluate_forecast(
    actual: Sequence[ActualMatch],
    tournament_predictions: Mapping,
    world_cup_probabilities: Sequence[Mapping],
    group_results: Mapping,
    representative_tournament: Mapping,
    knockout_probabilities: Mapping[int, "MatchProbabilities"] | None = None,
) -> dict:
    """Score the published forecast against what actually happened.

    ``knockout_probabilities`` (keyed by match number) holds the model's exact
    pre-tournament probabilities for each real knockout pairing; knockouts are
    then also scored on whether the model's favourite went through.
    """

    predicted_group = {
        frozenset((match["home_team"], match["away_team"])): match
        for match in tournament_predictions["matches"]
        if match["stage"] == "group"
    }

    group_rows = []
    for match in (m for m in actual if m.stage == "group"):
        prediction = predicted_group.get(frozenset((match.home_team, match.away_team)))
        if prediction is None:
            raise ValueError(f"No prediction for {match.home_team} v {match.away_team}")
        swapped = prediction["home_team"] != match.home_team
        probabilities = {
            "home": prediction["away_win_probability" if swapped else "home_win_probability"],
            "draw": prediction["draw_probability"],
            "away": prediction["home_win_probability" if swapped else "away_win_probability"],
        }
        predicted_goals = (
            (prediction["predicted_away_goals"], prediction["predicted_home_goals"])
            if swapped
            else (prediction["predicted_home_goals"], prediction["predicted_away_goals"])
        )
        favourite = max(probabilities, key=probabilities.__getitem__)
        brier = sum(
            (probabilities[key] - float(key == match.outcome)) ** 2 for key in probabilities
        )
        group_rows.append(
            {
                "match_number": match.match_number,
                "date": match.date,
                "group": match.group,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "outcome": match.outcome,
                "home_win_probability": probabilities["home"],
                "draw_probability": probabilities["draw"],
                "away_win_probability": probabilities["away"],
                "predicted_outcome": favourite,
                "predicted_home_goals": predicted_goals[0],
                "predicted_away_goals": predicted_goals[1],
                "outcome_hit": favourite == match.outcome,
                "exact_score_hit": predicted_goals == (match.home_score, match.away_score),
                "probability_of_actual_outcome": probabilities[match.outcome],
                "brier": brier,
            }
        )

    reached = actual_stage_reached(actual)
    probabilities_by_team = {row["team"]: row for row in world_cup_probabilities}
    qualification = {
        row["team"]: row["qualification_probability"]
        for rows in group_results["groups"].values()
        for row in rows
    }
    champion_probability = {team: row["champion_probability"] for team, row in probabilities_by_team.items()}
    final_probability = {
        team: row["champion_probability"] + row["runner_up_probability"]
        for team, row in probabilities_by_team.items()
    }

    team_rows = []
    for team, stage in sorted(reached.items(), key=lambda item: (-STAGE_ORDER[item[1]], -champion_probability[item[0]])):
        row = probabilities_by_team[team]
        team_rows.append(
            {
                "team": team,
                "actual_stage": stage,
                "qualification_probability": qualification[team],
                "semifinal_probability": row["semifinal_probability"],
                "final_probability": final_probability[team],
                "champion_probability": row["champion_probability"],
                "champion_rank": _rank(champion_probability, team),
            }
        )

    def reached_at_least(team: str, stage: str) -> bool:
        return STAGE_ORDER[reached[team]] >= STAGE_ORDER[stage]

    teams = list(reached)
    champion = next(m.winner for m in actual if m.stage == "final")
    runner_up = next(m.loser for m in actual if m.stage == "final")
    representative = representative_tournament["representative_tournament"]
    predicted_final = next(m for m in representative["bracket"] if m["round"] == "final")

    knockout_rows = []
    predicted_pairs_by_stage: dict[str, set[frozenset[str]]] = {}
    for match in representative["bracket"]:
        predicted_pairs_by_stage.setdefault(match["round"], set()).add(
            frozenset((match["home_team"], match["away_team"]))
        )
    predicted_teams_by_stage = {
        stage: {team for pair in pairs for team in pair} for stage, pairs in predicted_pairs_by_stage.items()
    }
    for match in (m for m in actual if m.stage != "group"):
        model = (knockout_probabilities or {}).get(match.match_number)
        model_fields = {}
        if model is not None:
            favourite = match.home_team if model.advance_a >= 0.5 else match.away_team
            model_fields = {
                "home_win_probability": model.win_a,
                "draw_probability": model.draw,
                "away_win_probability": model.win_b,
                "home_advance_probability": model.advance_a,
                "away_advance_probability": model.advance_b,
                "home_expected_goals": model.expected_goals_a,
                "away_expected_goals": model.expected_goals_b,
                "model_favourite": favourite,
                "favourite_advanced": favourite == match.winner,
                "probability_of_actual_winner": model.advance_a if match.winner == match.home_team else model.advance_b,
            }
        knockout_rows.append(
            {
                "match_number": match.match_number,
                "date": match.date,
                "stage": match.stage,
                "home_team": match.home_team,
                "away_team": match.away_team,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "shootout_winner": match.shootout_winner,
                "winner": match.winner,
                "pairing_predicted": frozenset((match.home_team, match.away_team))
                in predicted_pairs_by_stage.get(match.stage, set()),
                **model_fields,
            }
        )

    rounds = []
    for stage, count in KNOCKOUT_STAGES:
        if stage == "third_place_playoff":
            continue
        actual_teams = {
            team for m in actual if m.stage == stage for team in (m.home_team, m.away_team)
        }
        predicted_teams = predicted_teams_by_stage.get(stage, set())
        rounds.append(
            {
                "stage": stage,
                "teams": count * 2,
                "predicted_teams_correct": len(actual_teams & predicted_teams),
            }
        )

    n = len(group_rows)
    group_summary = {
        "matches": n,
        "outcome_hits": sum(row["outcome_hit"] for row in group_rows),
        "exact_score_hits": sum(row["exact_score_hit"] for row in group_rows),
        "mean_brier": sum(row["brier"] for row in group_rows) / n,
        "baseline_mean_brier": 2 / 3,
        "mean_log_loss": -sum(math.log(row["probability_of_actual_outcome"]) for row in group_rows) / n,
        "baseline_log_loss": math.log(3),
        "outcome_counts": {
            key: sum(row["outcome"] == key for row in group_rows) for key in ("home", "draw", "away")
        },
        "predicted_draws": sum(row["predicted_outcome"] == "draw" for row in group_rows),
    }

    scored_knockouts = [row for row in knockout_rows if "favourite_advanced" in row]
    knockout_summary = (
        {
            "matches": len(scored_knockouts),
            "favourite_advanced": sum(row["favourite_advanced"] for row in scored_knockouts),
            "advance_brier": sum((1 - row["probability_of_actual_winner"]) ** 2 for row in scored_knockouts)
            / len(scored_knockouts),
            "baseline_advance_brier": 0.25,
            "advance_log_loss": -sum(math.log(row["probability_of_actual_winner"]) for row in scored_knockouts)
            / len(scored_knockouts),
            "baseline_advance_log_loss": math.log(2),
            "method": "exact model probabilities for the real pairing, pre-tournament ratings",
        }
        if scored_knockouts
        else None
    )

    qualified_actual = {team for team in teams if reached_at_least(team, "round_of_32")}
    top_32_predicted = set(sorted(qualification, key=qualification.__getitem__, reverse=True)[:32])

    return {
        "metadata": {
            "scope": "world_cup_2026_forecast_vs_actual",
            "forecast_simulations": group_results["metadata"].get("simulations"),
            "actual_results_source": "github.com/martj42/international_results",
        },
        "summary": {
            "champion": champion,
            "runner_up": runner_up,
            "champion_probability": champion_probability[champion],
            "champion_rank": _rank(champion_probability, champion),
            "runner_up_rank": _rank(champion_probability, runner_up),
            "model_favourite": max(champion_probability, key=champion_probability.__getitem__),
            "model_favourite_stage": reached[max(champion_probability, key=champion_probability.__getitem__)],
            "predicted_final": [predicted_final["home_team"], predicted_final["away_team"]],
            "predicted_champion": representative["champion"],
            "final_pairing_predicted": frozenset((champion, runner_up))
            == frozenset((predicted_final["home_team"], predicted_final["away_team"])),
            "qualified_correct": len(qualified_actual & top_32_predicted),
            "qualified_total": len(qualified_actual),
            "qualification_brier": _brier_binary((qualification[t], t in qualified_actual) for t in teams),
            "qualification_baseline_brier": _brier_binary(
                (len(qualified_actual) / len(teams), t in qualified_actual) for t in teams
            ),
            "semifinal_brier": _brier_binary(
                (probabilities_by_team[t]["semifinal_probability"], reached_at_least(t, "semi_final")) for t in teams
            ),
            "semifinal_baseline_brier": _brier_binary((4 / len(teams), reached_at_least(t, "semi_final")) for t in teams),
        },
        "group_stage": {"summary": group_summary, "matches": group_rows},
        "knockout_rounds": rounds,
        "knockout_summary": knockout_summary,
        "knockout_matches": knockout_rows,
        "teams": team_rows,
    }
