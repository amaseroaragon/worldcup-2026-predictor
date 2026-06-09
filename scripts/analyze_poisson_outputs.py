from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.core.match import _expected_goals_feature_kwargs
from src.prediction.core.poisson import expected_goals_from_elo, score_probability
from src.prediction.pipeline import PredictionInputs, load_prediction_inputs
from src.prediction.settings import DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH


DEFAULT_DIAGNOSTICS_DIR = ROOT_DIR / "outputs" / "diagnostics"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze current Poisson lambdas and generated match predictions."
    )
    parser.add_argument(
        "--predictions-input",
        type=Path,
        default=DEFAULT_TOURNAMENT_PREDICTIONS_JSON_PATH,
        help="Existing tournament_predictions.json produced by the prediction pipeline.",
    )
    parser.add_argument(
        "--output-format",
        choices=("json", "csv"),
        help="Optionally export diagnostics as JSON or CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Its suffix can be used instead of --output-format.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of frequent predicted scores to print.",
    )
    parser.add_argument(
        "--show-matches",
        action="store_true",
        help="Print one diagnostic row per match before aggregate statistics.",
    )
    return parser.parse_args()


def load_prediction_records(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    matches = payload.get("matches")
    if not isinstance(matches, list) or not matches:
        raise ValueError(f"Prediction file must contain a non-empty 'matches' list: {path}")

    return payload.get("metadata", {}), matches


def build_diagnostic_rows(
    matches: list[dict[str, Any]],
    inputs: PredictionInputs,
) -> list[dict[str, Any]]:
    rows = []
    for match in matches:
        home_team = str(match["home_team"])
        away_team = str(match["away_team"])
        home_lambda, away_lambda = expected_goals_from_elo(
            inputs.ratings[home_team],
            inputs.ratings[away_team],
            **_expected_goals_feature_kwargs(
                team_a=home_team,
                team_b=away_team,
                team_strength_ratings=inputs.team_strength_ratings,
                recent_form_ratings=inputs.recent_form_ratings,
                squad_strength_ratings=inputs.squad_strength_ratings,
            ),
        )
        predicted_home_goals = int(match["predicted_home_goals"])
        predicted_away_goals = int(match["predicted_away_goals"])
        predicted_score = f"{predicted_home_goals}-{predicted_away_goals}"

        rows.append(
            {
                "match_id": match.get("match_id"),
                "stage": match.get("stage"),
                "round": match.get("round"),
                "group": match.get("group"),
                "home_team": home_team,
                "away_team": away_team,
                "home_lambda": home_lambda,
                "away_lambda": away_lambda,
                "total_lambda": home_lambda + away_lambda,
                "lambda_diff": home_lambda - away_lambda,
                "home_win_probability": float(match["home_win_probability"]),
                "draw_probability": float(match["draw_probability"]),
                "away_win_probability": float(match["away_win_probability"]),
                "predicted_score": predicted_score,
                "predicted_score_probability": score_probability(
                    predicted_home_goals,
                    predicted_away_goals,
                    home_lambda,
                    away_lambda,
                ),
                "predicted_winner": match.get("predicted_winner"),
                "prediction_source": match.get("source"),
            }
        )

    return rows


def aggregate_diagnostics(rows: list[dict[str, Any]], top: int = 20) -> dict[str, Any]:
    if not rows:
        raise ValueError("At least one diagnostic row is required")
    if top <= 0:
        raise ValueError("--top must be positive")

    score_counts = Counter(str(row["predicted_score"]) for row in rows)
    predicted_draws = sum(
        row["predicted_score"].split("-", maxsplit=1)[0]
        == row["predicted_score"].split("-", maxsplit=1)[1]
        for row in rows
    )

    distribution = [
        {
            "predicted_score": score,
            "count": count,
            "percentage": count / len(rows) * 100,
        }
        for score, count in score_counts.most_common()
    ]
    return {
        "matches_analyzed": len(rows),
        "mean_home_lambda": mean(float(row["home_lambda"]) for row in rows),
        "mean_away_lambda": mean(float(row["away_lambda"]) for row in rows),
        "mean_total_lambda": mean(float(row["total_lambda"]) for row in rows),
        "mean_draw_probability": mean(float(row["draw_probability"]) for row in rows),
        "predicted_draw_percentage": predicted_draws / len(rows) * 100,
        "predicted_score_distribution": distribution,
        "top_predicted_scores": distribution[:top],
    }


def resolve_output_path(output: Path | None, output_format: str | None) -> tuple[Path, str] | None:
    if output is None and output_format is None:
        return None

    if output_format is None:
        output_format = output.suffix.lower().lstrip(".") if output is not None else ""
        if output_format not in {"json", "csv"}:
            raise ValueError("Output path must end in .json or .csv")

    output_path = output or DEFAULT_DIAGNOSTICS_DIR / f"poisson_diagnostics.{output_format}"
    if output_path.suffix.lower() != f".{output_format}":
        raise ValueError("Output path suffix must match --output-format")
    return output_path, output_format


def export_diagnostics(
    output_path: Path,
    output_format: str,
    metadata: dict[str, Any],
    aggregate: dict[str, Any],
    rows: list[dict[str, Any]],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        payload = {
            "metadata": metadata,
            "aggregate": aggregate,
            "matches": rows,
        }
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        return

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def print_match_rows(rows: list[dict[str, Any]]) -> None:
    print("\nMatch diagnostics:")
    for row in rows:
        stage = row["round"] or row["stage"] or "unknown"
        print(
            f"{row['match_id']}: {row['home_team']} vs {row['away_team']} | "
            f"stage={stage} | lambdas={row['home_lambda']:.4f}-{row['away_lambda']:.4f} | "
            f"probabilities={row['home_win_probability']:.4f}/"
            f"{row['draw_probability']:.4f}/{row['away_win_probability']:.4f} | "
            f"predicted_score={row['predicted_score']}"
        )


def print_aggregate(aggregate: dict[str, Any], top: int) -> None:
    print("\nAggregate Poisson diagnostics:")
    print(f"Matches analyzed: {aggregate['matches_analyzed']}")
    print(f"Mean home_lambda: {aggregate['mean_home_lambda']:.4f}")
    print(f"Mean away_lambda: {aggregate['mean_away_lambda']:.4f}")
    print(f"Mean total_lambda: {aggregate['mean_total_lambda']:.4f}")
    print(f"Mean draw_probability: {aggregate['mean_draw_probability']:.4f}")
    print(f"Predicted draw percentage: {aggregate['predicted_draw_percentage']:.2f}%")

    print("\nPredicted score distribution:")
    for item in aggregate["predicted_score_distribution"]:
        print(
            f"  {item['predicted_score']:>5}: {item['count']:>3} "
            f"({item['percentage']:.2f}%)"
        )

    print(f"\nTop {top} predicted scores:")
    for rank, item in enumerate(aggregate["top_predicted_scores"], start=1):
        print(
            f"  {rank:>2}. {item['predicted_score']:>5}: {item['count']:>3} "
            f"({item['percentage']:.2f}%)"
        )


def main() -> None:
    args = parse_args()
    metadata, matches = load_prediction_records(args.predictions_input)
    inputs = load_prediction_inputs()
    rows = build_diagnostic_rows(matches, inputs)
    aggregate = aggregate_diagnostics(rows, top=args.top)

    if args.show_matches:
        print_match_rows(rows)
    print_aggregate(aggregate, args.top)

    resolved_output = resolve_output_path(args.output, args.output_format)
    if resolved_output is not None:
        output_path, output_format = resolved_output
        export_diagnostics(
            output_path,
            output_format,
            {
                "predictions_input": str(args.predictions_input),
                "prediction_metadata": metadata,
                "lambda_source": "expected_goals_from_elo with current base prediction inputs",
                "probability_source": "existing tournament prediction records",
                "interpretation_note": (
                    "Exported Monte Carlo probabilities may include dynamic Elo updates; "
                    "diagnostic lambdas are a reproducible base-ratings snapshot."
                ),
            },
            aggregate,
            rows,
        )
        print(f"\nGenerated diagnostics file: {output_path}")


if __name__ == "__main__":
    main()
