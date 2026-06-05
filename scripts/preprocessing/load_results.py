import pandas as pd

from src.prediction.settings import PATH_SETTINGS


RAW_DATA_DIR = PATH_SETTINGS.raw_data_dir
RESULTS_PATH = PATH_SETTINGS.raw_results_path


def main() -> None:
    """Print a quick overview of the raw results dataset."""

    df = pd.read_csv(RESULTS_PATH)

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


if __name__ == "__main__":
    main()
