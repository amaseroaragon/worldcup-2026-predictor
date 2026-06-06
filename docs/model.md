# Model

This document explains the current model components. It is intended as an implementation guide, not a full mathematical specification.

## Elo

The Elo system lives in `src/elo/` and produces historical team ratings.

### Expected Score

For each match, the model computes an expected score from the rating difference between the two teams. This represents the pre-match expectation for each side.

### Match Result

The actual result is converted into Elo scores:

- Win: `1.0`
- Draw: `0.5`
- Loss: `0.0`

### K-factor

The K-factor controls how much ratings move after a match.

The project currently supports:

- A base K-factor in `src/elo/config.py`.
- Tournament-specific K-factors in `data/external/tournament_k_factors.json`.

When match context is available, `src/elo/context.py` tries to resolve the K-factor from the external tournament mapping. If no context is found, the base behavior is preserved.

### Importance

Match context is represented by `MatchContext`. World Cup simulations pass context such as group stage or knockout stage. In the current implementation, World Cup K-factor resolution is tournament-based.

### Margin of Victory

Goal difference is used as a conservative multiplier on the Elo update. The multiplier is capped to avoid extreme rating changes from single matches.

## Poisson

The match engine uses a Poisson distribution to simulate goals.

Flow:

1. Convert Elo and team metrics into expected goals.
2. Compute probabilities for `0..max_goals`.
3. Sample a score for each team.
4. Resolve the match result according to the stage.

Group-stage matches can end in draws. Knockout matches always produce a winner; if the simulated score is tied, a probabilistic tiebreaker is applied.

## Expected Goals

Expected goals combine:

- Elo difference.
- The team's attack rating.
- The opponent's defense rating.
- The team's recent form.
- The team's squad strength.

Expected goals are bounded between minimum and maximum values to avoid unstable extremes.

## Attack Rating

Attack rating is computed from clean historical results. It compares a team's scoring production against the global goals-per-team-match average.

In the model, an attack rating above `1.0` increases that team's expected goals. A value below `1.0` reduces them.

## Defense Rating

Defense rating is computed from historical goals conceded. In the current implementation, it acts on the opponent's expected goals.

Practical interpretation:

- Teams conceding more than average tend to increase the opponent's expected goals.
- Teams conceding less than average tend to reduce them.

Ratings are clipped to configured bounds for stability.

## Recent Form

Recent form is based on recent points:

- Win: 3 points.
- Draw: 1 point.
- Loss: 0 points.

The implementation keeps 5-, 10-, and 20-match windows and applies recency weighting. The simulation uses a primary window configured in `settings.py`.

Recent form influences expected goals through a conservative multiplier. If a team lacks enough matches for the selected window, the effect is neutral.

## Squad Strength

Squad strength uses team values from `data/external/teams_value.json`.

Current process:

1. Read team values.
2. Apply a logarithmic transform.
3. Compare each team against the mean.
4. Clip ratings to conservative bounds.

The result acts as an additional expected-goals multiplier. Missing squad strength is treated as neutral.

The calibrated default squad-strength weight is `0.30`.

## Knockout Tiebreaker

If a knockout match has a tied simulated score, the model calculates the probability that team A advances.

That probability blends:

- Elo expected score.
- Relative expected-goals advantage.

The expected-goals component is controlled by `TIEBREAKER_EXPECTED_GOALS_WEIGHT`.

## Dynamic Elo in Simulations

During a tournament simulation, the model can update a local copy of Elo ratings after group-stage and knockout matches.

This does not modify `data/processed/elo_rankings.csv`; it only affects later matches within the same simulation. The relevant flags are defined in `settings.py` and re-exported through `config.py`.

## V5.5 Calibration

The default model configuration was calibrated through historical backtesting against:

- FIFA World Cup 2018.
- FIFA World Cup 2022.
- UEFA Euro 2024.

The calibration process compared model-component variants, controlled weight combinations, and repeated evaluations across multiple random seeds. The selected default configuration is:

- `recent_form_weight = 0.15` unchanged.
- `squad_strength_weight = 0.30`, increased from `0.10`.
- Dynamic Elo enabled for the group stage and knockout stage, unchanged.

The selected configuration provided a conservative improvement while retaining Dynamic Elo. Calibration experiments remain isolated from the main prediction pipeline.

## Current Limits

- The model does not use real-time data.
- The frontend is not implemented yet.
- Probabilities depend on the quality of historical results and external configuration.
- Monte Carlo performance is still a V5 optimization target.
