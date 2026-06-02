from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = ROOT_DIR / "data" / "raw"

results_path = RAW_DATA_DIR / "results.csv"

df = pd.read_csv(results_path)


print("=" * 50)
print("DATASET OVERVIEW")
print("=" * 50)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)


print("\n" + "=" * 50)
print("MISSING VALUES")
print("=" * 50)

print(df.isnull().sum())


print("\n" + "=" * 50)
print("DATE RANGE")
print("=" * 50)

print("Min date:", df["date"].min())
print("Max date:", df["date"].max())


print("\n" + "=" * 50)
print("TEAMS")
print("=" * 50)

teams = set(df["home_team"]).union(set(df["away_team"]))

print("Total unique teams:", len(teams))

print("\nSample teams:")
print(sorted(list(teams))[:30])


print("\n" + "=" * 50)
print("TOURNAMENTS")
print("=" * 50)

print("Unique tournaments:", df["tournament"].nunique())

print("\nTop tournaments:")
print(df["tournament"].value_counts().head(20))