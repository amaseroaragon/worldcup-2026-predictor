from src.prediction.core.models import MatchResult
from src.prediction.core.standings import build_group_standings


def test_build_group_standings_calculates_points_and_goals():
    results = [
        MatchResult("Spain", "France", 2, 1, "Spain", False, "regular_time"),
        MatchResult("Brazil", "Japan", 0, 0, None, True, "draw"),
        MatchResult("Spain", "Brazil", 1, 1, None, True, "draw"),
    ]

    standings = build_group_standings(results)
    spain = next(row for row in standings if row.team == "Spain")
    brazil = next(row for row in standings if row.team == "Brazil")

    assert spain.played == 2
    assert spain.points == 4
    assert spain.goals_for == 3
    assert spain.goals_against == 2
    assert spain.goal_difference == 1
    assert brazil.points == 2


def test_build_group_standings_orders_by_points_goal_difference_goals_for():
    results = [
        MatchResult("Spain", "France", 2, 0, "Spain", False, "regular_time"),
        MatchResult("Brazil", "Japan", 1, 0, "Brazil", False, "regular_time"),
        MatchResult("Spain", "Brazil", 0, 1, "Brazil", False, "regular_time"),
        MatchResult("France", "Japan", 3, 0, "France", False, "regular_time"),
    ]

    standings = build_group_standings(results)

    assert [row.team for row in standings[:2]] == ["Brazil", "France"]
