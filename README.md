# World Cup 2026 Predictor

A statistical forecast of the FIFA World Cup 2026, made before the tournament and scored against what actually happened. Python model, bilingual Next.js site (EN/ES).

## Results

| | |
|---|---|
| Final | Predicted Spain v Argentina, which was the real final (Spain won 1–0) |
| Champion | Spain was the model's #2 at 11%; its favourite, Argentina (17%), was runner-up |
| Teams called per round | Last 32: 25/32 · Last 16: 12/16 · QF: 6/8 · SF: 3/4 · Final: 2/2 |
| Matches | Group favourite won 41/72 (random ≈ 24) · knockout favourite went through 24/32 |
| Backtest | 2018, 2022 World Cups and Euro 2024: real champion in the top 5 in 14/15 runs |

## Methodology

1. **Elo ratings** from 49,405 international results since 1872.
2. **Team metrics**: attack and defence relative to Elo, recent form and squad market value.
3. **Match model**: expected goals per team, scores drawn from a Poisson distribution.
4. **Monte Carlo**: the full 48-team tournament simulated 10,000 times.

Details: [docs/methodology.md](docs/methodology.md) · [docs/architecture.md](docs/architecture.md)

## Run

```bash
cd frontend && npm install && npm run dev
```
