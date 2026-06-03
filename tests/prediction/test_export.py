import pandas as pd
import pytest

from src.prediction.export import (
    PROBABILITY_COLUMNS,
    export_probabilities,
    probabilities_to_dataframe,
    validate_probability_output,
)


def sample_probabilities() -> dict:
    return {
        "Team 1": {"champion": 0.2, "runner_up": 0.3, "semifinal": 0.5},
        "Team 2": {"champion": 0.8, "runner_up": 0.1, "semifinal": 0.9},
    }


def test_probabilities_to_dataframe_returns_expected_columns_sorted_by_champion_probability():
    df = probabilities_to_dataframe(sample_probabilities())

    assert df.columns.tolist() == PROBABILITY_COLUMNS
    assert df["team"].tolist() == ["Team 2", "Team 1"]


def test_probabilities_to_dataframe_exports_float_probabilities_between_zero_and_one():
    df = probabilities_to_dataframe(sample_probabilities())

    for column in ["champion_probability", "runner_up_probability", "semifinal_probability"]:
        assert pd.api.types.is_float_dtype(df[column])
        assert df[column].between(0, 1).all()


def test_export_probabilities_writes_csv(tmp_path):
    output_path = tmp_path / "world_cup_probabilities.csv"

    df = export_probabilities(sample_probabilities(), output_path)
    written = pd.read_csv(output_path)

    assert output_path.exists()
    assert written.columns.tolist() == PROBABILITY_COLUMNS
    assert written["team"].tolist() == df["team"].tolist()


def test_validate_probability_output_accepts_valid_output():
    df = probabilities_to_dataframe(sample_probabilities())

    validate_probability_output(df)


def test_validate_probability_output_rejects_missing_columns():
    df = pd.DataFrame({"team": ["Team 1"]})

    with pytest.raises(ValueError, match="Missing probability output columns"):
        validate_probability_output(df)


def test_validate_probability_output_rejects_probabilities_outside_range():
    df = probabilities_to_dataframe(sample_probabilities())
    df.loc[0, "champion_probability"] = 1.2

    with pytest.raises(ValueError, match="between 0 and 1"):
        validate_probability_output(df)
