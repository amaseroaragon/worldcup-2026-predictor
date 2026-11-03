/**
 * Backtest results for the selected model configuration
 * (recent_form_weight = 0.15, squad_strength_weight = 0.30, dynamic Elo on).
 *
 * Source: data/backtest/multiseed_combination_results.csv, configuration "C",
 * 5 seeds (1, 7, 21, 42, 99) × 1,000 simulations per tournament.
 * Values are averages across seeds. Copy them by hand if the backtest is re-run.
 */

export type BacktestTournament = {
  id: string;
  name: string;
  teams: number;
  realChampion: string;
  modelFavorite: string;
  favoriteProbability: number;
  realChampionProbability: number;
  realChampionRankBySeed: number[];
  top3Hits: number;
  top5Hits: number;
  seeds: number;
  brierChampion: number;
  brierSemifinal: number;
};

export const BACKTEST_TOURNAMENTS: BacktestTournament[] = [
  {
    id: "world_cup_2018",
    name: "World Cup 2018",
    teams: 32,
    realChampion: "France",
    modelFavorite: "Germany",
    favoriteProbability: 0.2266,
    realChampionProbability: 0.0866,
    realChampionRankBySeed: [6, 5, 5, 5, 4],
    top3Hits: 0,
    top5Hits: 4,
    seeds: 5,
    brierChampion: 0.0302,
    brierSemifinal: 0.109,
  },
  {
    id: "world_cup_2022",
    name: "World Cup 2022",
    teams: 32,
    realChampion: "Argentina",
    modelFavorite: "Brazil",
    favoriteProbability: 0.203,
    realChampionProbability: 0.1784,
    realChampionRankBySeed: [2, 2, 2, 2, 2],
    top3Hits: 5,
    top5Hits: 5,
    seeds: 5,
    brierChampion: 0.0235,
    brierSemifinal: 0.0989,
  },
  {
    id: "euro_2024",
    name: "Euro 2024",
    teams: 24,
    realChampion: "Spain",
    modelFavorite: "France",
    favoriteProbability: 0.2394,
    realChampionProbability: 0.1554,
    realChampionRankBySeed: [2, 2, 3, 2, 2],
    top3Hits: 5,
    top5Hits: 5,
    seeds: 5,
    brierChampion: 0.0347,
    brierSemifinal: 0.063,
  },
];

export const MODEL_CONFIG = {
  recentFormWeight: 0.15,
  squadStrengthWeight: 0.3,
  dynamicElo: true,
} as const;

/** Probability a uniform "every team is equal" baseline gives each team to win. */
export function uniformChampionProbability(teams: number): number {
  return 1 / teams;
}

export function backtestSummary() {
  const runs = BACKTEST_TOURNAMENTS.reduce((total, t) => total + t.seeds, 0);
  const top5 = BACKTEST_TOURNAMENTS.reduce((total, t) => total + t.top5Hits, 0);
  const top3 = BACKTEST_TOURNAMENTS.reduce((total, t) => total + t.top3Hits, 0);
  const liftVsUniform =
    BACKTEST_TOURNAMENTS.reduce(
      (total, t) => total + t.realChampionProbability / uniformChampionProbability(t.teams),
      0,
    ) / BACKTEST_TOURNAMENTS.length;

  return { runs, top5, top3, liftVsUniform, tournaments: BACKTEST_TOURNAMENTS.length };
}
