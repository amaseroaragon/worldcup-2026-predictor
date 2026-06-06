# World Cup 2026 Predictor

World Cup 2026 Predictor is a Python backend for simulating the FIFA World Cup 2026. It combines Elo ratings, Poisson score simulation, team strength metrics, tournament bracket logic, and Monte Carlo aggregation to estimate match outcomes and tournament probabilities.

## What It Does

- Builds historical Elo ratings from international match results.
- Computes team metrics such as attack/defense ratings, recent form, and squad strength.
- Simulates group-stage and knockout-stage matches.
- Resolves the World Cup 2026 bracket, including best third-place teams.
- Runs Monte Carlo tournament simulations.
- Exports probability and match prediction JSON files.

## Project Structure

```text
data/                 Raw, processed, and external data files
src/data/             Data normalization and validation
src/elo/              Historical Elo calculation
src/prediction/core/     Match engine, Poisson, standings, and core models
src/prediction/metrics/ Team strength, recent form, and squad strength
src/prediction/tournament_flow/ Tournament, knockout, and Monte Carlo logic
src/prediction/io/       JSON export and output validation
scripts/                 Operational entry points
tests/                   Unit and contract tests
docs/                    Detailed documentation
```

## Main Pipeline

```text
Historical results
-> cleaned results
-> Elo history
-> current Elo rankings
-> team metrics
-> match simulation
-> tournament simulation
-> Monte Carlo aggregation
-> JSON outputs
```

## Run

Install the package and dependencies in your own environment:

```bash
python -m pip install -e .
```

The project requires Python 3.11 or newer.

Build clean results:

```bash
python scripts/build_clean_results.py
```

Build Elo history and rankings:

```bash
python scripts/elo/build_elo_ratings.py
python scripts/elo/export_elo_ratings.py
```

Run the full prediction pipeline:

```bash
python scripts/prediction/run_prediction_pipeline.py --simulations 1000 --seed 42
```

Run tests:

```bash
python -m pytest -q
```

## Outputs

- `outputs/predictions/team_metrics.json`
- `outputs/predictions/world_cup_probabilities.json`
- `outputs/predictions/tournament_predictions.json`

## Documentation

- [Architecture](docs/architecture.md)
- [Model](docs/model.md)
- [Monte Carlo](docs/monte_carlo.md)

## Current Status

The project is currently in V5.5. Model calibration was validated through backtesting on World Cup 2018, World Cup 2022, and Euro 2024, including model variants and multiple random seeds.

The selected default configuration keeps `recent_form_weight = 0.15` and Dynamic Elo enabled, and uses the calibrated `squad_strength_weight = 0.30`. The frontend is planned for V6 and is not implemented yet.
