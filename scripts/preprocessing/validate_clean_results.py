import pandas as pd

from src.data.validation import CLEAN_RESULTS_REQUIRED_COLUMNS, validate_clean_results_dataframe
from src.prediction.settings import DEFAULT_CLEAN_RESULTS_PATH


CLEAN_RESULTS_PATH = DEFAULT_CLEAN_RESULTS_PATH


def main() -> None:
    """Print and validate basic properties of the clean results dataset."""

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

    critical_nulls = df[CLEAN_RESULTS_REQUIRED_COLUMNS].isnull().sum()

    if critical_nulls.sum() > 0:
        raise ValueError(
            f"Critical null values found:\n{critical_nulls}"
        )

    if (df["home_score"] < 0).any() or (df["away_score"] < 0).any():
        raise ValueError("Negative scores found.")

    if (df["home_team"] == df["away_team"]).any():
        raise ValueError("Some matches have the same home and away team.")

    validate_clean_results_dataframe(df)

    print("\nValidation passed successfully.")


if __name__ == "__main__":
    main()
