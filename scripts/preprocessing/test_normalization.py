from pathlib import Path

import pandas as pd

from src.data.normalization import (
    normalize_teams_in_dataframe,
)


ROOT_DIR = Path(__file__).resolve().parents[2]

RESULTS_PATH = (
    ROOT_DIR
    / "data"
    / "raw"
    / "results.csv"
)


df = pd.read_csv(RESULTS_PATH)

print("=" * 50)
print("BEFORE NORMALIZATION")
print("=" * 50)

teams_before = set(df["home_team"]).union(set(df["away_team"]))

print("Total unique teams:", len(teams_before))


df = normalize_teams_in_dataframe(df)


print("\n" + "=" * 50)
print("AFTER NORMALIZATION")
print("=" * 50)

teams_after = set(df["home_team"]).union(set(df["away_team"]))

print("Total unique teams:", len(teams_after))
