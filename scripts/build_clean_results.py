import pandas as pd

from src.data.normalization import normalize_teams_in_dataframe
from src.prediction.settings import PATH_SETTINGS


RAW_RESULTS_PATH = PATH_SETTINGS.raw_results_path
PROCESSED_DIR = PATH_SETTINGS.processed_data_dir
CLEAN_RESULTS_PATH = PATH_SETTINGS.clean_results_path


def build_clean_results() -> pd.DataFrame:
    """Build the normalized historical results dataset."""

    df = pd.read_csv(RAW_RESULTS_PATH)

    df["date"] = pd.to_datetime(df["date"])

    df = normalize_teams_in_dataframe(df)

    df = df[
        [
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "tournament",
            "city",
            "country",
            "neutral",
        ]
    ].copy()

    df = df.dropna(
        subset=[
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        ]
    )

    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["neutral"] = df["neutral"].astype(bool)

    df = df.sort_values("date").reset_index(drop=True)

    return df


def main() -> None:
    """Generate the processed clean results CSV."""

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = build_clean_results()
    df.to_csv(CLEAN_RESULTS_PATH, index=False)

    print("Clean results saved to:")
    print(CLEAN_RESULTS_PATH)


if __name__ == "__main__":
    main()
