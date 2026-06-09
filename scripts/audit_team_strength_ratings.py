from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean, median


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.settings import TEAM_STRENGTH_MAX_RATING, TEAM_STRENGTH_MIN_RATING


DEFAULT_INPUT = ROOT_DIR / "outputs" / "predictions" / "world_cup_team_metrics.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit attack and defense rating calibration.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.input.open(encoding="utf-8") as file:
        teams = json.load(file)["teams"]

    attacks = [float(team["attack_rating"]) for team in teams]
    defenses = [float(team["defense_rating"]) for team in teams]
    print_rankings("Top 10 attacks", teams, "attack_rating", reverse=True)
    print_rankings("Top 10 defenses", teams, "defense_rating", reverse=False)
    print_distribution("Attack rating distribution", attacks)
    print_distribution("Defense rating distribution", defenses)


def print_rankings(title: str, teams: list[dict], field: str, *, reverse: bool) -> None:
    print(f"\n{title}:")
    for rank, team in enumerate(sorted(teams, key=lambda row: row[field], reverse=reverse)[:10], 1):
        print(f"{rank:2}. {team['team']:<22} {team[field]:.4f}")


def print_distribution(title: str, values: list[float]) -> None:
    minimum = min(values)
    maximum = max(values)
    print(f"\n{title}:")
    print(f"count={len(values)} mean={mean(values):.4f} median={median(values):.4f}")
    print(f"min={minimum:.4f} max={maximum:.4f}")
    print(f"saturated_min={sum(value == TEAM_STRENGTH_MIN_RATING for value in values)}")
    print(f"saturated_max={sum(value == TEAM_STRENGTH_MAX_RATING for value in values)}")
    print("values=" + ", ".join(f"{value:.4f}" for value in sorted(values)))


if __name__ == "__main__":
    main()
