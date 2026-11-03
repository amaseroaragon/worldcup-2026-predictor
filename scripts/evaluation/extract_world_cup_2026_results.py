"""Extract the 104 real World Cup 2026 matches from the public results dataset.

Source: https://github.com/martj42/international_results (results.csv, shootouts.csv).
Download both files, then run:

    python scripts/evaluation/extract_world_cup_2026_results.py results.csv shootouts.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.evaluation.world_cup_2026 import build_actual_matches, write_actual_matches

DEFAULT_OUTPUT = ROOT_DIR / "data" / "actual" / "world_cup_2026_results.csv"
GROUPS_PATH = ROOT_DIR / "data" / "external" / "groups.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("results", type=Path, help="martj42 results.csv")
    parser.add_argument("shootouts", type=Path, help="martj42 shootouts.csv")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    with args.results.open(encoding="utf-8", newline="") as file:
        results = list(csv.DictReader(file))
    with args.shootouts.open(encoding="utf-8", newline="") as file:
        shootouts = list(csv.DictReader(file))
    groups = json.loads(GROUPS_PATH.read_text(encoding="utf-8"))["groups"]

    matches = build_actual_matches(results, shootouts, groups)
    write_actual_matches(matches, args.output)
    print(f"Saved {len(matches)} matches to {args.output}")


if __name__ == "__main__":
    main()
