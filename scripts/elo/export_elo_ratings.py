import pandas as pd

from src.elo.export import get_latest_ratings
from src.prediction.settings import PATH_SETTINGS


def main() -> None:
    """Export the latest Elo rating per team."""

    input_path = PATH_SETTINGS.elo_history_path
    output_path = PATH_SETTINGS.elo_rankings_path

    elo_history = pd.read_csv(input_path, parse_dates=["date"])

    rankings = get_latest_ratings(elo_history)

    rankings.to_csv(output_path, index=False)

    print(f"Elo rankings saved to: {output_path}")


if __name__ == "__main__":
    main()
