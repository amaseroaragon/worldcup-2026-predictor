from scripts.analyze_poisson_outputs import aggregate_diagnostics


def test_diagnostics_count_scores_contradicting_displayed_outcome():
    rows = [
        {
            "predicted_score": "1-0",
            "round": None,
            "stage": "group",
            "draw_probability": 0.2,
            "home_lambda": 1.4,
            "away_lambda": 1.0,
            "total_lambda": 2.4,
            "predicted_winner": "Home",
            "score_contradicts_displayed_outcome": False,
            "competitive_draw_selected": False,
            "match_id": "M1",
            "home_team": "Home",
            "away_team": "Away",
            "home_win_probability": 0.6,
            "away_win_probability": 0.2,
        },
        {
            "predicted_score": "0-1",
            "round": None,
            "stage": "group",
            "draw_probability": 0.2,
            "home_lambda": 1.4,
            "away_lambda": 1.0,
            "total_lambda": 2.4,
            "predicted_winner": "Home",
            "score_contradicts_displayed_outcome": True,
            "competitive_draw_selected": False,
            "match_id": "M2",
            "home_team": "Home",
            "away_team": "Away",
            "home_win_probability": 0.6,
            "away_win_probability": 0.2,
        },
    ]

    aggregate = aggregate_diagnostics(rows)

    assert aggregate["scores_contradicting_displayed_outcome"] == 1
    assert aggregate["number_of_competitive_draws_selected"] == 0
