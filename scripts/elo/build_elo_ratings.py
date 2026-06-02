import pandas as pd

from src.elo.processor import process_matches


def main():
    input_path = "data/processed/clean_results.csv"
    output_path = "data/processed/elo_history.csv"

    df = pd.read_csv(input_path)

    elo_history = process_matches(df)

    elo_history.to_csv(output_path, index=False)

    print(f"Elo history saved to: {output_path}")


if __name__ == "__main__":
    main()