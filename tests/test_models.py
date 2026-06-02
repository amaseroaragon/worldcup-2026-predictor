from src.prediction.models import MatchFixture, SimulationConfig, TournamentOutcome


def test_match_fixture_stores_basic_match_metadata():
    fixture = MatchFixture(
        match_id="A1",
        stage="group",
        group="A",
        team_a="Spain",
        team_b="France",
    )

    assert fixture.match_id == "A1"
    assert fixture.group == "A"
    assert fixture.team_a == "Spain"
    assert fixture.team_b == "France"


def test_simulation_config_defaults_are_pre_tournament_friendly():
    config = SimulationConfig()

    assert config.n_simulations == 1000
    assert config.fixed_elo is True
    assert config.max_goals == 10


def test_tournament_outcome_defaults_to_empty_collections():
    outcome = TournamentOutcome()

    assert outcome.champion is None
    assert outcome.group_outcomes == {}
    assert outcome.match_results == []
