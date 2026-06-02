from collections import defaultdict

import pandas as pd

from src.elo.config import BASE_ELO, K_FACTOR, HOME_ADVANTAGE
from src.elo.update import match_result, update_rating


def process_matches(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process matches chronologically and generate Elo history.
    """

    df = df.sort_values("date").reset_index(drop=True)
    ratings = defaultdict(lambda: BASE_ELO)

    history = []

    for _, row in df.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]

        home_score = row["home_score"]
        away_score = row["away_score"]

        neutral = row.get("neutral", False)

        # Current ratings
        home_elo_before = ratings[home_team]
        away_elo_before = ratings[away_team]

        # Apply home advantage
        adjusted_home_elo = home_elo_before
        if not neutral:
            adjusted_home_elo += HOME_ADVANTAGE

        # Match result
        home_result, away_result = match_result(
            home_score,
            away_score,
        )

        # Updated ratings
        home_elo_after = update_rating(
            rating=adjusted_home_elo,
            opponent_rating=away_elo_before,
            actual_score=home_result,
            k_factor=K_FACTOR,
        )

        away_elo_after = update_rating(
            rating=away_elo_before,
            opponent_rating=adjusted_home_elo,
            actual_score=away_result,
            k_factor=K_FACTOR,
        )

        # Remove temporary home advantage inflation
        if not neutral:
            home_elo_after -= HOME_ADVANTAGE

        # Store ratings
        ratings[home_team] = home_elo_after
        ratings[away_team] = away_elo_after

        history.append(
            {
                "date": row["date"],
                "home_team": home_team,
                "away_team": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "home_elo_before": round(home_elo_before, 2),
                "away_elo_before": round(away_elo_before, 2),
                "home_elo_after": round(home_elo_after, 2),
                "away_elo_after": round(away_elo_after, 2),
            }
        )

    return pd.DataFrame(history)
