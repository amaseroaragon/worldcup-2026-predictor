from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]

CLEAN_RESULTS_PATH = ROOT_DIR / "data" / "processed" / "clean_results.csv"


def main() -> None:
    df = pd.read_csv(CLEAN_RESULTS_PATH)

    print("=" * 50)
    print("CLEAN RESULTS VALIDATION")
    print("=" * 50)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nData types:")
    print(df.dtypes)

    print("\nDate range:")
    print(df["date"].min(), "->", df["date"].max())

    teams = set(df["home_team"]).union(set(df["away_team"]))
    print("\nUnique teams:")
    print(len(teams))

    print("\nDuplicated rows:")
    print(df.duplicated().sum())

    print("\nTop tournaments:")
    print(df["tournament"].value_counts().head(20))

    print("\nSample teams:")
    print(sorted(list(teams))[:50])

    critical_columns = [
        "date",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "tournament",
        "neutral",
    ]

    critical_nulls = df[critical_columns].isnull().sum()

    if critical_nulls.sum() > 0:
        raise ValueError(
            f"Critical null values found:\n{critical_nulls}"
        )

    if (df["home_score"] < 0).any() or (df["away_score"] < 0).any():
        raise ValueError("Negative scores found.")

    if df["home_team"].equals(df["away_team"]):
        raise ValueError("Some matches have the same home and away team.")

    print("\nValidation passed successfully.")


if __name__ == "__main__":
    main()