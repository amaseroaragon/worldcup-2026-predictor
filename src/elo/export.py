import pandas as pd


def get_latest_ratings(elo_history: pd.DataFrame) -> pd.DataFrame:
    """
    Build latest Elo rating per team from Elo match history.
    """

    home_ratings = elo_history[["date", "home_team", "home_elo_after"]].rename(
        columns={
            "home_team": "team",
            "home_elo_after": "elo",
        }
    )

    away_ratings = elo_history[["date", "away_team", "away_elo_after"]].rename(
        columns={
            "away_team": "team",
            "away_elo_after": "elo",
        }
    )

    all_ratings = pd.concat([home_ratings, away_ratings], ignore_index=True)

    latest = (
        all_ratings.sort_values("date")
        .groupby("team", as_index=False)
        .last()
        .sort_values("elo", ascending=False)
        .reset_index(drop=True)
    )

    latest.insert(0, "rank", latest.index + 1)

    return latest