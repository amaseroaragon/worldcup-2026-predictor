import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GROUPS_PATH = PROJECT_ROOT / "data/external/groups.json"
WORLD_CUP_TEAM_METRICS_PATH = (
    PROJECT_ROOT / "outputs/predictions/world_cup_team_metrics.json"
)
GROUP_RESULTS_PATH = PROJECT_ROOT / "outputs/predictions/group_results.json"
REPRESENTATIVE_TOURNAMENT_PATH = (
    PROJECT_ROOT / "outputs/predictions/representative_tournament.json"
)


def load_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def test_world_cup_team_metrics_contract():
    assert WORLD_CUP_TEAM_METRICS_PATH.exists()

    configured_groups = load_json(GROUPS_PATH)["groups"]
    expected_teams = {
        team
        for teams in configured_groups.values()
        for team in teams
    }
    payload = load_json(WORLD_CUP_TEAM_METRICS_PATH)
    teams = payload["teams"]

    assert {record["team"] for record in teams} == expected_teams
    assert all(record["group"] in configured_groups for record in teams)
    assert all(
        record["team"] in configured_groups[record["group"]]
        for record in teams
    )


def test_group_results_contract():
    assert GROUP_RESULTS_PATH.exists()

    payload = load_json(GROUP_RESULTS_PATH)
    groups = payload["groups"]

    assert len(groups) == 12
    assert set(groups) == set("ABCDEFGHIJKL")
    for standings in groups.values():
        assert len(standings) == 4
        assert [record["position"] for record in standings] == [1, 2, 3, 4]
        for record in standings:
            probability = record.get("qualification_probability")
            assert probability is None or 0 <= probability <= 1


def test_representative_tournament_contract():
    assert REPRESENTATIVE_TOURNAMENT_PATH.exists()

    payload = load_json(REPRESENTATIVE_TOURNAMENT_PATH)["representative_tournament"]
    assert len(payload["groups"]) == 12
    assert len(payload["qualified"]["round_of_32"]) == 32
    assert len(payload["bracket"]) == 32
    assert payload["champion"] is not None

    for standings in payload["groups"].values():
        assert [row["position"] for row in standings] == [1, 2, 3, 4]
        assert standings == sorted(
            standings,
            key=lambda row: (
                -row["points"],
                -row["goal_difference"],
                -row["goals_for"],
                row["team"],
            ),
        )
