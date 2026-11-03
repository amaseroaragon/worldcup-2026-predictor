import type { MatchRow } from "@/components/matches/types";
import type { ForecastVsActual } from "@/lib/types";

/**
 * All 104 real matches with the model's pre-tournament view, in calendar order.
 * Group matches use the simulated win/draw/loss frequencies; knockouts use the model's
 * exact probabilities for the real pairing and are judged on who went through.
 */
export function buildMatchRows(report: ForecastVsActual): MatchRow[] {
  const group: MatchRow[] = report.group_stage.matches.map((m) => ({
    id: m.match_number,
    date: m.date,
    roundKey: "group",
    home: m.home_team,
    away: m.away_team,
    homeScore: m.home_score,
    awayScore: m.away_score,
    winner: m.outcome === "home" ? m.home_team : m.outcome === "away" ? m.away_team : null,
    probabilities: { home: m.home_win_probability, draw: m.draw_probability, away: m.away_win_probability },
    actual: m.outcome,
    predictedScore: `${m.predicted_home_goals}–${m.predicted_away_goals}`,
    hit: m.outcome_hit,
  }));

  const knockout: MatchRow[] = report.knockout_matches.map((m) => ({
    id: m.match_number,
    date: m.date,
    roundKey: m.stage,
    home: m.home_team,
    away: m.away_team,
    homeScore: m.home_score,
    awayScore: m.away_score,
    winner: m.winner,
    probabilities: { home: m.home_win_probability, draw: m.draw_probability, away: m.away_win_probability },
    knockout: {
      homeAdvance: m.home_advance_probability,
      awayAdvance: m.away_advance_probability,
      favourite: m.model_favourite,
      pairingPredicted: m.pairing_predicted,
      shootoutWinner: m.shootout_winner,
    },
    hit: m.favourite_advanced,
  }));

  return [...group, ...knockout].toSorted((a, b) => a.id - b.id);
}
