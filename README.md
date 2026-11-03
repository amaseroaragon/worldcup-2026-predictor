# World Cup 2026 Predictor

A statistical forecast of the FIFA World Cup 2026. It uses Elo ratings, a Poisson goal model and 10,000 Monte Carlo tournament simulations, and was backtested on the 2018 and 2022 World Cups and Euro 2024. A Next.js site presents the results.

**How it did:** the model's projected final, Spain v Argentina, is exactly the final that was played. It gave Spain 11% (#2) and Argentina 17% (#1), and Spain won 1–0. It called 25 of the 32 knockout qualifiers and 3 of the 4 semi-finalists. The favourite won 41 of the 72 group matches, and the model's favourite went through in 24 of the 32 knockout ties.
**Backtest:** on the 2018 and 2022 World Cups and Euro 2024, the eventual champion was in the model's top five in 14 of 15 seeded runs.

## How it works

```text
49k international results (1872–2026)
  → Elo ratings (K-factor by competition, capped margin of victory)
  → team metrics: attack/defence vs. Elo expectation, recent form, squad value
  → expected goals per match → Poisson score simulation
  → full 48-team tournament × 10,000 (best thirds, bracket, in-tournament Elo updates)
  → JSON outputs → static Next.js site

after the tournament: real results (data/actual/) → forecast vs. actual evaluation
```

Details, formula and limitations: [docs/methodology.md](docs/methodology.md). The site's `/method` page has the short version.

## Stack

- **Model:** Python 3.11, pandas, numpy, pytest.
- **Site:** Next.js 16 (App Router, fully static), React 19, Tailwind CSS 4, TypeScript. It is bilingual: `/en` and `/es`, and `/` redirects by browser language. No chart library: the charts are plain HTML/CSS.

The site reads JSON files that the pipeline copies into `frontend/public/data/`. There is no API or server-side model.

## Run locally

```bash
# Model (from the repo root)
python -m pip install -e .
python scripts/build_clean_results.py
python scripts/elo/build_elo_ratings.py
python scripts/elo/export_elo_ratings.py
python scripts/prediction/run_prediction_pipeline.py --simulations 10000 --seed 42   # also syncs JSON to the frontend

# Site
cd frontend
npm install
npm run dev          # http://localhost:3000
```

Forecast vs. actual, Elo export for the site (run after the pipeline; both are picked up by the sync):

```bash
# results.csv and shootouts.csv from github.com/martj42/international_results
python scripts/evaluation/extract_world_cup_2026_results.py results.csv shootouts.csv
python scripts/elo/export_world_cup_elo.py
python scripts/evaluation/evaluate_world_cup_2026.py
python scripts/frontend/sync_frontend_data.py
```

The frontend already ships with the latest outputs, so you can skip the model steps if you only want to run the site.

Tests and lint:

```bash
python -m pytest -q
cd frontend && npm run lint && npm run build
```

## Repository layout

```text
data/          raw results, processed Elo, tournament config (data/external), backtest datasets,
               real World Cup 2026 results (data/actual)
src/elo/       historical Elo computation
src/prediction/ match model, team metrics, tournament flow, Monte Carlo, exports
src/backtesting/ backtest metrics and model variants
src/evaluation/ forecast vs. real World Cup 2026 results
scripts/       entry points (preprocessing, Elo, prediction, backtesting, frontend sync)
outputs/       generated predictions, backtest outputs and diagnostics
frontend/      Next.js site
tests/         unit and data-contract tests
docs/          methodology and architecture notes
```

See [docs/architecture.md](docs/architecture.md) for the module map and data contracts.
