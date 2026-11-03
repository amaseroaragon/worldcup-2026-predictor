"""Export pre-tournament Elo ratings of the 48 World Cup 2026 teams as JSON for the frontend."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.settings import PATH_SETTINGS

GROUPS_PATH = ROOT_DIR / "data" / "external" / "groups.json"
OUTPUT_PATH = ROOT_DIR / "outputs" / "predictions" / "world_cup_elo_ratings.json"


def build_world_cup_elo(rankings: list[dict[str, str]], groups: dict[str, list[str]]) -> list[dict]:
    group_by_team = {team: group for group, teams in groups.items() for team in teams}
    ordered = sorted(rankings, key=lambda row: float(row["elo"]), reverse=True)
    world_rank = {row["team"]: index + 1 for index, row in enumerate(ordered)}
    teams = [row for row in ordered if row["team"] in group_by_team]

    missing = set(group_by_team) - {row["team"] for row in teams}
    if missing:
        raise ValueError(f"Missing Elo ratings for: {', '.join(sorted(missing))}")

    return [
        {
            "team": row["team"],
            "group": group_by_team[row["team"]],
            "elo": round(float(row["elo"]), 1),
            "world_rank": world_rank[row["team"]],
            "field_rank": index + 1,
            "rating_date": row["date"],
        }
        for index, row in enumerate(teams)
    ]


def main() -> None:
    with Path(PATH_SETTINGS.elo_rankings_path).open(encoding="utf-8", newline="") as file:
        rankings = list(csv.DictReader(file))
    groups = json.loads(GROUPS_PATH.read_text(encoding="utf-8"))["groups"]

    payload = {
        "metadata": {"source": "data/processed/elo_rankings.csv", "scope": "world_cup_2026_teams"},
        "teams": build_world_cup_elo(rankings, groups),
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {len(payload['teams'])} Elo ratings to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
