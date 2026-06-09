from scripts.analyze_poisson_outputs import aggregate_diagnostics


def test_diagnostics_count_scores_contradicting_most_probable_outcome():
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
            "score_contradicts_most_probable_outcome": False,
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
            "score_contradicts_most_probable_outcome": True,
        },
    ]

    aggregate = aggregate_diagnostics(rows)

    assert aggregate["scores_contradicting_most_probable_outcome"] == 1
