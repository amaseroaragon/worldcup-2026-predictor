import pandas as pd

from src.data import normalization


def test_normalize_team_name_uses_mapping_when_team_has_former_name():
    mapping = {"Swaziland": "Eswatini"}

    assert normalization.normalize_team_name("Swaziland", mapping) == "Eswatini"


def test_normalize_team_name_keeps_team_when_not_in_mapping():
    mapping = {"Swaziland": "Eswatini"}

    assert normalization.normalize_team_name("Spain", mapping) == "Spain"


def test_normalize_teams_in_dataframe_updates_home_and_away_teams(monkeypatch):
    monkeypatch.setattr(
        normalization,
        "load_team_name_mapping",
        lambda: {"Swaziland": "Eswatini", "Burma": "Myanmar"},
    )
    df = pd.DataFrame(
        {
            "home_team": ["Swaziland", "Spain"],
            "away_team": ["France", "Burma"],
        }
    )

    normalized = normalization.normalize_teams_in_dataframe(df)

    assert normalized["home_team"].tolist() == ["Eswatini", "Spain"]
    assert normalized["away_team"].tolist() == ["France", "Myanmar"]
