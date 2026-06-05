import pandas as pd

from src.prediction.settings import DEFAULT_FORMER_NAMES_PATH


FORMER_NAMES_PATH = DEFAULT_FORMER_NAMES_PATH


def load_team_name_mapping() -> dict:
    """Load historical-to-current team name mappings."""

    df = pd.read_csv(FORMER_NAMES_PATH)
    return dict(zip(df["former"], df["current"], strict=True))


def normalize_team_name(team_name: str, mapping: dict) -> str:
    """Normalize a team name using a provided mapping."""

    return mapping.get(team_name, team_name)


def normalize_teams_in_dataframe(
    df: pd.DataFrame,
    home_col: str = "home_team",
    away_col: str = "away_team",
) -> pd.DataFrame:
    """Normalize home and away team names in a dataframe."""

    mapping = load_team_name_mapping()
    df[home_col] = df[home_col].apply(lambda team: normalize_team_name(team, mapping))
    df[away_col] = df[away_col].apply(lambda team: normalize_team_name(team, mapping))

    return df
