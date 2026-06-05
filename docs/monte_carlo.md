# Monte Carlo

Monte Carlo is the mechanism that turns individual tournament simulations into aggregate tournament probabilities.

## What It Does

`src/prediction/tournament_flow/monte_carlo.py` repeatedly runs `simulate_tournament_once`.

Each run returns a `TournamentOutcome` containing:

- Champion.
- Runner-up.
- Semifinalists.
- Teams reaching tracked rounds.
- Group-stage eliminations.
- Match results.
- Group outcomes.

## What One Simulation Represents

One simulation is one possible World Cup 2026 outcome under the current model.

It includes:

1. Group-stage fixture construction.
2. Group-stage match simulation.
3. Group standings calculation.
4. Qualified-team and best third-place resolution.
5. Knockout placeholder resolution.
6. Knockout match simulation.
7. Local dynamic Elo updates when enabled.
8. Champion, runner-up, and stage tracking.

## Group Stage

The group stage uses configured fixtures from `group_matches.json`. The fixture builder also supports legacy round-robin generation when called without explicit match configuration.

Each group must have:

- 4 teams.
- 6 matches.

Standings are sorted by:

1. Points.
2. Goal difference.
3. Goals for.
4. Team name.

## Best Third-Place Teams

Third-place teams are ranked with the same main table criteria:

1. Points.
2. Goal difference.
3. Goals for.
4. Team name.

The model then uses `third_place_combinations.json` to resolve official best third-place placeholders in the knockout bracket.

## Knockout Stage

`knockouts.json` defines matches with placeholders. Placeholders can refer to:

- Group winners.
- Group runners-up.
- Third-place teams.
- Winners of previous matches.
- Runners-up or losers of previous matches where applicable.

Before each knockout match is simulated, its fixture is resolved using known results from the same simulation.

Knockout matches always produce a winner. If the Poisson score is tied, the model applies the knockout tiebreaker.

## Aggregation

After each simulation, Monte Carlo updates counters by team:

- `champion`
- `runner_up`
- `semifinal`

At the end, each counter is divided by the total number of simulations. The result is exported as `world_cup_probabilities.json`.

Conceptual example:

```text
simulations = 1000
Team A champion count = 125
champion_probability = 125 / 1000 = 0.125
```

## Interpreting Probabilities

Probabilities are not certainties or absolute rankings. They represent frequencies across simulated tournament outcomes under the current model assumptions.

- `champion_probability`: how often the team wins the tournament.
- `runner_up_probability`: how often the team finishes runner-up.
- `semifinal_probability`: how often the team reaches the semifinals.

A high probability means the team frequently reaches that outcome given the current metrics, bracket configuration, and model randomness.

## Aggregated Bracket

`tournament_predictions.json` is not a single simulation. It is an aggregated predicted bracket.

- Group-stage predictions are built from fixed scheduled matches.
- Knockout predictions resolve a likely bracket from aggregate outcomes.
- If a specific matchup is missing from simulated outcomes, the model can use a direct prediction fallback to complete the bracket.

Relevant fields include:

- `appearance_count`
- `appearance_probability`
- `source`
- `most_common_score`
- `average_home_goals`
- `average_away_goals`

## Reproducibility

Scripts accept `--seed`. With the same configuration, seed, and number of simulations, results should be reproducible in the same environment.

Example:

```bash
python scripts/prediction/run_prediction_pipeline.py --simulations 1000 --seed 42
```

## Cost and Optimization

Runtime grows mainly with the number of simulations. Monte Carlo performance optimization remains a V5 target, especially for larger simulation counts and faster iteration.
