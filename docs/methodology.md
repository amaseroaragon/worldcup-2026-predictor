# Methodology

## 1. Elo ratings (`src/elo/`)

Ratings are rebuilt chronologically from `data/processed/clean_results.csv`. Each update uses:

- the standard Elo expected score;
- a K-factor that depends on the competition (`data/external/tournament_k_factors.json`; friendlies 10, World Cup highest);
- home advantage of 80 points for non-neutral venues;
- a margin-of-victory multiplier, capped so a single blowout cannot move a rating too far.

## 2. Team metrics (`src/prediction/metrics/`)

| Metric | Definition | Effect on expected goals |
|---|---|---|
| Attack / defence | Goals scored and conceded divided by the goals Elo expected against those opponents, over the last 20 matches. Shrunk 50% towards 1.0 and clipped to [0.65, 1.35]. | Direct multiplier |
| Recent form | Recency-weighted points per match over the last 10 matches (5 and 20 are also exported). | `1 + 0.15 · (form − 1)` |
| Squad strength | Log of squad market value (`teams_value.json`) relative to the field mean, clipped to [0.85, 1.15]. | `1 + 0.30 · (squad − 1)` |

A missing metric is treated as neutral (1.0).

## 3. Match model (`src/prediction/core/poisson.py`)

```text
λ_A = 1.35 · exp(0.0015 · (Elo_A − Elo_B)) · Attack_A · Defence_B · Form_A · Squad_A
λ_A clipped to [0.2, 3.5]
```

Each team's goals are drawn from Poisson(λ). In the group stage a draw is a valid result. In a knockout match a level score is resolved by a tiebreaker that blends the Elo expected score with the relative expected-goals advantage (weight 0.35).

## 4. Tournament simulation (`src/prediction/tournament_flow/`)

One simulation plays the whole tournament:

1. The 72 group matches (`group_matches.json`). Standings are ordered by points, goal difference, goals for, then name.
2. The eight best third-placed teams are ranked by the same criteria and placed using the official combination table (`third_place_combinations.json`).
3. The knockout bracket (`knockouts.json`): placeholders are resolved from earlier results and every match produces a winner.
4. Elo ratings are updated on a local copy after every match (dynamic Elo). `data/processed/elo_rankings.csv` is never modified.

Monte Carlo (`monte_carlo.py`) repeats this N times and counts outcomes per team. The published run uses N = 10,000 and seed 42.

### Outputs (`outputs/predictions/`)

| File | Content |
|---|---|
| `world_cup_probabilities.json` | Champion, runner-up and semi-final probability per team |
| `group_results.json` | Qualification probability, expected points, goals and finishing position per team |
| `tournament_predictions.json` | Win/draw/loss probabilities for all 104 matches (knockout slots show the most frequent pairing) |
| `representative_tournament.json` | One coherent tournament built from the most likely result in each match, used for the bracket |
| `team_metrics.json`, `world_cup_team_metrics.json` | Model inputs per team |

Probabilities are frequencies across simulations, not certainties. The representative tournament is one plausible storyline: its final pairing occurs in under 5% of simulations.

## 5. Backtesting and calibration (`scripts/backtesting/`)

The pipeline is re-run on historical datasets in `data/backtest/<tournament>/`, with data cut off at each tournament's opening day. Metrics come from `src/backtesting/metrics.py`: the real champion's probability and rank, top-3/top-5 hit, and Brier scores per stage.

Six configurations were compared across five seeds (`data/backtest/multiseed_combination_*.csv`). The selected configuration keeps form weight 0.15 and dynamic Elo, and raises the squad weight from 0.10 to 0.30. It gives about a 1% lower mean Brier score, a deliberately conservative change.

| Tournament | Champion | Model rank | Champion's probability | Model favourite |
|---|---|---|---|---|
| World Cup 2018 | France | 5 | 8.7% | Germany (23%) |
| World Cup 2022 | Argentina | 2 | 17.8% | Brazil (20%) |
| Euro 2024 | Spain | 2 | 15.5% | France (24%) |

These values are mirrored by hand in `frontend/lib/model-validation.ts`. Update that file if the backtest is re-run.

## 6. Forecast vs. actual (`src/evaluation/world_cup_2026.py`)

After the tournament the real results are extracted from the public dataset the raw data comes from (`github.com/martj42/international_results`) into `data/actual/world_cup_2026_results.csv`. Rows are assigned to rounds by calendar order. Every round is then checked: its teams must be the previous round's winners, and the third-place playoff must be played by the semi-final losers. Knockout scores include extra time; level games are decided by the shootout file.

`scripts/evaluation/evaluate_world_cup_2026.py` writes `outputs/predictions/forecast_vs_actual.json`. Nothing feeds back into the model.

- **Group stage (72 matches):** whether the model's most likely outcome happened, the 3-way Brier score and log loss. Baselines: 0.667 and ln 3.
- **Knockouts:** the simulation only has probabilities for pairings it produced, so `src/evaluation/match_probabilities.py` computes the model's exact probabilities for each *real* pairing. It reuses the model's expected goals, Poisson score matrix and knockout tiebreaker with pre-tournament ratings, which is what 10,000 runs converge to; it agrees with the simulated opening match to within 0.2 points. Because knockout scores include extra time, knockouts are scored on who went through, not on the 90-minute result. Teams reached per round and exact pairings are also reported.
- **Teams:** binary Brier scores for qualification and semi-final reach, against an equal-odds baseline.

| | Result |
|---|---|
| Final pairing | Spain v Argentina, as projected (3.9% of simulations) |
| Champion | Spain, model #2 at 11.4% (the model picked Argentina) |
| Teams called per round | R32 25/32 · R16 12/16 · QF 6/8 · SF 3/4 · Final 2/2 |
| Group favourite won | 41/72 (random ≈ 24); exact score 5/72 |
| Group Brier / log loss | 0.528 / 0.894 (baselines 0.667 / 1.099) |
| Draws | 20 happened; the model never made a draw the most likely outcome |
| Knockout favourite went through | 24/32; Brier 0.166 (coin flip 0.25), log loss 0.507 (0.693) |

`scripts/elo/export_world_cup_elo.py` also exports the pre-tournament Elo of the 48 teams (`world_cup_elo_ratings.json`) for the site.

## Limitations

- No injuries, suspensions, line-ups or travel effects.
- Market values favour teams with players in the top European leagues.
- No explicit host advantage in the 2026 simulation.
- Three backtested tournaments is a small sample.
- Pre-tournament forecast only; it does not update with real results.
- A draw is never the single most likely outcome, which caps group-stage accuracy.
