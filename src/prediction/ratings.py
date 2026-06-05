from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.prediction.settings import DEFAULT_ELO_RANKINGS_PATH

REQUIRED_RATING_COLUMNS = {"team", "elo"}


def load_ratings(path: str | Path = DEFAULT_ELO_RANKINGS_PATH) -> dict[str, float]:
    """Load team Elo ratings from a rankings CSV file."""

    ratings = pd.read_csv(path)
    missing_columns = REQUIRED_RATING_COLUMNS - set(ratings.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required Elo ranking columns: {missing}")

    return dict(zip(ratings["team"], ratings["elo"].astype(float), strict=True))
