from pathlib import Path

import pandas as pd


ELO_HISTORY_PATH = Path("data/processed/elo_history.csv")
ELO_RANKINGS_PATH = Path("data/processed/elo_rankings.csv")


def validate_file_exists(path: Path) -> None:
    """Validate that a required output file exists."""

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")


def validate_not_empty(df: pd.DataFrame, name: str) -> None:
    """Validate that a dataframe contains at least one row."""

    if df.empty:
        raise ValueError(f"{name} is empty")


def validate_no_null_ratings(df: pd.DataFrame, columns: list[str], name: str) -> None:
    """Validate that selected rating columns contain no nulls."""

    null_counts = df[columns].isna().sum()
    invalid = null_counts[null_counts > 0]

    if not invalid.empty:
        raise ValueError(f"{name} contains null ratings:\n{invalid}")


def validate_unique_ranked_teams(rankings: pd.DataFrame) -> None:
    """Validate that each ranked team appears only once."""

    duplicated = rankings[rankings["team"].duplicated()]

    if not duplicated.empty:
        raise ValueError(f"Duplicated teams in rankings:\n{duplicated}")


def validate_rankings_sorted(rankings: pd.DataFrame) -> None:
    """Validate that rankings are sorted by descending Elo."""

    if not rankings["elo"].is_monotonic_decreasing:
        raise ValueError("Rankings are not sorted by descending Elo")


def validate_rating_range(rankings: pd.DataFrame) -> None:
    """Validate that Elo ratings are in a plausible range."""

    invalid = rankings[(rankings["elo"] < 800) | (rankings["elo"] > 2300)]

    if not invalid.empty:
        raise ValueError(f"Suspicious Elo ratings found:\n{invalid}")


def validate_ranked_teams_exist_in_history(history: pd.DataFrame, rankings: pd.DataFrame) -> None:
    """Validate that ranked teams also appear in Elo history."""

    history_teams = set(history["home_team"]).union(set(history["away_team"]))
    ranking_teams = set(rankings["team"])

    missing = ranking_teams - history_teams

    if missing:
        raise ValueError(f"Ranked teams missing from history: {sorted(missing)}")


def main() -> None:
    """Run all Elo output validations."""

    validate_file_exists(ELO_HISTORY_PATH)
    validate_file_exists(ELO_RANKINGS_PATH)

    history = pd.read_csv(ELO_HISTORY_PATH)
    rankings = pd.read_csv(ELO_RANKINGS_PATH)

    validate_not_empty(history, "elo_history.csv")
    validate_not_empty(rankings, "elo_rankings.csv")

    validate_no_null_ratings(
        history,
        [
            "home_elo_before",
            "away_elo_before",
            "home_elo_after",
            "away_elo_after",
        ],
        "elo_history.csv",
    )

    validate_no_null_ratings(
        rankings,
        ["elo"],
        "elo_rankings.csv",
    )

    validate_unique_ranked_teams(rankings)
    validate_rankings_sorted(rankings)
    validate_rating_range(rankings)
    validate_ranked_teams_exist_in_history(history, rankings)

    print("Elo output validation passed.")


if __name__ == "__main__":
    main()
