import pandas as pd

from src.elo.processor import process_matches
from src.prediction.settings import PATH_SETTINGS


def main() -> None:
    """Build chronological Elo history from clean match results."""

    input_path = PATH_SETTINGS.clean_results_path
    output_path = PATH_SETTINGS.elo_history_path

    df = pd.read_csv(input_path)

    elo_history = process_matches(df)

    elo_history.to_csv(output_path, index=False)

    print(f"Elo history saved to: {output_path}")


if __name__ == "__main__":
    main()
