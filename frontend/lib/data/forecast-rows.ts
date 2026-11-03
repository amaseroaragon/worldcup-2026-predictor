import "server-only";

import type { ForecastRow } from "@/components/tables/forecast-table";

import { loadEloRatings, loadForecastVsActual } from "./load-prediction-data";

/** Every team with its pre-tournament odds, Elo and real outcome, ranked by title odds. */
export async function loadForecastRows(): Promise<ForecastRow[]> {
  const [{ teams }, elo] = await Promise.all([loadForecastVsActual(), loadEloRatings()]);
  const eloByTeam = new Map(elo.teams.map((row) => [row.team, row]));

  return teams
    .map((row) => {
      const rating = eloByTeam.get(row.team);
      return {
        team: row.team,
        group: rating?.group ?? "",
        elo: rating?.elo ?? 0,
        eloRank: rating?.field_rank ?? 0,
        champion: row.champion_probability,
        advance: row.qualification_probability,
        semifinal: row.semifinal_probability,
        final: row.final_probability,
        stage: row.actual_stage,
      };
    })
    .toSorted((a, b) => b.champion - a.champion || b.advance - a.advance);
}
