# Architecture

This document describes the current backend structure and data flow of World Cup 2026 Predictor.

## Project Layout

```text
worldcup-2026-predictor/
  data/
    raw/
    processed/
    external/
  src/
    data/
    elo/
    prediction/
  scripts/
    preprocessing/
    elo/
    prediction/
  frontend/
  outputs/
  tests/
```

## `data/`

`data/` contains source inputs and generated artifacts.

- `data/raw/results.csv`: original historical match results.
- `data/processed/clean_results.csv`: normalized historical results used by Elo and metric builders.
- `data/processed/elo_history.csv`: match-by-match Elo history.
- `data/processed/elo_rankings.csv`: latest Elo rating per team.
- `outputs/predictions/team_metrics.json`: exported team metrics.
- `data/external/`: tournament configuration and auxiliary data.

External configuration files:

- `groups.json`: World Cup 2026 groups.
- `group_matches.json`: ordered group-stage match schedule.
- `knockouts.json`: knockout bracket structure.
- `third_place_combinations.json`: best third-place placeholder resolution table.
- `tournament_k_factors.json`: tournament-specific Elo K-factors.
- `teams_value.json`: squad market values used for squad strength.
- `former_names.csv`: historical team-name normalization mapping.

## `src/`

`src/` contains the main application logic.

### `src/data/`

- `normalization.py`: normalizes team names using `former_names.csv`.
- `validation.py`: validates clean result datasets and cross-file World Cup configuration consistency.

### `src/elo/`

- `expected.py`: Elo expected score.
- `update.py`: Elo result conversion, margin-of-victory factor, and rating update.
- `context.py`: K-factor loading and context resolution.
- `processor.py`: chronological Elo processing from clean match results.
- `export.py`: latest-rating extraction.
- `config.py`: base Elo constants.

### `src/prediction/`

Prediction logic is grouped by responsibility.

```text
prediction/
  core/
  metrics/
  tournament_flow/
  io/
  config.py
  pipeline.py
  ratings.py
  settings.py
```

#### `prediction/core/`

Low-level prediction building blocks:

- `models.py`: dataclasses for fixtures, results, standings, outcomes, and simulation config.
- `match.py`: single-match simulation and knockout tiebreaker.
- `poisson.py`: Poisson probabilities, expected goals, and score matrices.
- `probabilities.py`: Elo win/draw/loss probabilities.
- `standings.py`: group standings.
- `dynamic_elo.py`: local Elo updates during simulations.
- `results.py`: result helpers.

#### `prediction/metrics/`

Team-level model features:

- `team_strength.py`: attack/defense ratings and team metric export.
- `recent_form.py`: recency-weighted form ratings.
- `squad_strength.py`: squad market-value strength ratings.

#### `prediction/tournament_flow/`

Tournament orchestration:

- `fixtures.py`: group-stage fixture construction.
- `group_stage.py`: group-stage simulation.
- `knockout.py`: knockout fixture resolution and simulation.
- `simulation.py`: one full tournament simulation.
- `monte_carlo.py`: repeated tournament simulation and probability aggregation.
- `bracket_predictions.py`: aggregated predicted bracket construction.
- `match_predictions.py`: match-result to prediction conversion.
- `prediction_summary.py`: aggregation helpers.

#### `prediction/io/`

- `exports.py`: JSON exports and probability output validation.

#### Root prediction modules

- `config.py`: external configuration loaders.
- `settings.py`: project paths and model flags.
- `pipeline.py`: shared prediction input loading.
- `ratings.py`: processed Elo ranking loader.

## `scripts/`

Scripts are operational entry points.

### Preprocessing

- `scripts/build_clean_results.py`: builds `data/processed/clean_results.csv`.
- `scripts/preprocessing/load_results.py`: prints a quick raw-data overview.
- `scripts/preprocessing/validate_clean_results.py`: validates clean-result dataset properties.

### Elo

- `scripts/elo/build_elo_ratings.py`: builds `elo_history.csv`.
- `scripts/elo/export_elo_ratings.py`: builds `elo_rankings.csv`.
- `scripts/elo/validate_elo_outputs.py`: validates Elo outputs.

### Prediction

- `scripts/prediction/run_prediction_pipeline.py`: runs the full prediction pipeline, including team metrics, Monte Carlo probabilities, and match predictions.

### Backtesting and Calibration

- `scripts/backtesting/run_backtest.py`: runs the prediction pipeline against a historical tournament dataset.
- `scripts/backtesting/evaluate_model_variants.py`: compares declarative model-component variants.
- `scripts/backtesting/calibration_experiments.py`: evaluates individual calibration parameters.
- `scripts/backtesting/combination_experiments.py`: evaluates controlled parameter combinations.
- `scripts/backtesting/multiseed_combination_experiments.py`: validates selected combinations across multiple seeds.

Calibration used World Cup 2018, World Cup 2022, and Euro 2024. The selected default keeps `recent_form_weight = 0.15` and Dynamic Elo enabled, while setting `squad_strength_weight = 0.30`.

## Data Flow

```text
data/raw/results.csv
  -> scripts/build_clean_results.py
data/processed/clean_results.csv
  -> scripts/elo/build_elo_ratings.py
data/processed/elo_history.csv
  -> scripts/elo/export_elo_ratings.py
data/processed/elo_rankings.csv
  -> scripts/prediction/run_prediction_pipeline.py
data/external/*.json
  -> config loaders
metrics + Elo + tournament config
  -> tournament simulation
  -> Monte Carlo
  -> outputs/predictions/*.json
```

## Important Contracts

- Every team in `groups.json` must exist in Elo rankings and squad values.
- `group_matches.json` must define six matches per group.
- `knockouts.json` must define a resolvable bracket.
- `third_place_combinations.json` must cover valid best third-place group combinations.
- Monte Carlo does not mutate processed Elo rankings; dynamic Elo updates are local to each simulation.
