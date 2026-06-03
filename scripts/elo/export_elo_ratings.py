import pandas as pd

from src.elo.export import get_latest_ratings


def main() -> None:
    """Export the latest Elo rating per team."""

    input_path = "data/processed/elo_history.csv"
    output_path = "data/processed/elo_rankings.csv"

    elo_history = pd.read_csv(input_path, parse_dates=["date"])

    rankings = get_latest_ratings(elo_history)

    rankings.to_csv(output_path, index=False)

    print(f"Elo rankings saved to: {output_path}")


if __name__ == "__main__":
    main()
