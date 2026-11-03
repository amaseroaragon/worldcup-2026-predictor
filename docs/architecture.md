# Architecture

## Data flow

```text
data/raw/results.csv
  → scripts/build_clean_results.py         → data/processed/clean_results.csv
  → scripts/elo/build_elo_ratings.py       → data/processed/elo_history.csv
  → scripts/elo/export_elo_ratings.py      → data/processed/elo_rankings.csv
  → scripts/prediction/run_prediction_pipeline.py
        + data/external/*.json (groups, fixtures, bracket, K-factors, squad values)
        → outputs/predictions/*.json
        → frontend/public/data/*.json      (scripts/frontend/sync_frontend_data.py)

after the tournament
  martj42 results.csv + shootouts.csv
  → scripts/evaluation/extract_world_cup_2026_results.py → data/actual/world_cup_2026_results.csv
  → scripts/evaluation/evaluate_world_cup_2026.py        → outputs/predictions/forecast_vs_actual.json
  data/processed/elo_rankings.csv
  → scripts/elo/export_world_cup_elo.py                  → outputs/predictions/world_cup_elo_ratings.json
```

The sync copies the two post-tournament files when they exist.

## Modules

| Path | Responsibility |
|---|---|
| `src/data/` | Team-name normalisation, dataset and config validation |
| `src/elo/` | Expected score, K-factor context, rating updates, chronological processing |
| `src/prediction/core/` | Data models, Poisson, single-match simulation, standings, dynamic Elo |
| `src/prediction/metrics/` | Attack/defence, recent form, squad strength |
| `src/prediction/tournament_flow/` | Group stage, knockouts, one-tournament simulation, Monte Carlo, aggregated and representative brackets |
| `src/prediction/io/` | JSON exports and output validation |
| `src/prediction/settings.py` | All model weights, bounds and paths (re-exported via `config.py`) |
| `src/backtesting/` | Backtest metrics and model-variant definitions |
| `src/evaluation/` | Real-result extraction, validation and forecast-vs-actual scoring |
| `frontend/` | Static Next.js site. Loaders live in `frontend/lib/data/`, shared types in `frontend/lib/types/` |

## Contracts

- Every team in `groups.json` must exist in the Elo rankings and in `teams_value.json`.
- Each group has 4 teams and 6 fixtures in `group_matches.json`.
- `knockouts.json` must resolve to a single bracket. `third_place_combinations.json` must cover every valid set of qualifying third places.
- Probabilities are exported as numbers in [0, 1]. The frontend never edits the synchronised JSON.
