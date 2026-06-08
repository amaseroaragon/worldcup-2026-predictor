import type { TournamentPredictionMatch } from "@/lib/types";

export type ProjectedGroupStats = {
  points: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
};

export function calculateProjectedGroupStats(
  matches: TournamentPredictionMatch[],
): Record<string, ProjectedGroupStats> {
  const stats: Record<string, ProjectedGroupStats> = {};

  for (const match of matches) {
    if (match.stage !== "group") continue;

    stats[match.home_team] ??= { points: 0, goalsFor: 0, goalsAgainst: 0, goalDifference: 0 };
    stats[match.away_team] ??= { points: 0, goalsFor: 0, goalsAgainst: 0, goalDifference: 0 };

    if (match.predicted_home_goals === null || match.predicted_away_goals === null) continue;

    stats[match.home_team].goalsFor += match.predicted_home_goals;
    stats[match.home_team].goalsAgainst += match.predicted_away_goals;
    stats[match.away_team].goalsFor += match.predicted_away_goals;
    stats[match.away_team].goalsAgainst += match.predicted_home_goals;

    if (match.predicted_home_goals > match.predicted_away_goals) {
      stats[match.home_team].points += 3;
    } else if (match.predicted_home_goals < match.predicted_away_goals) {
      stats[match.away_team].points += 3;
    } else {
      stats[match.home_team].points += 1;
      stats[match.away_team].points += 1;
    }
  }

  for (const teamStats of Object.values(stats)) {
    teamStats.goalDifference = teamStats.goalsFor - teamStats.goalsAgainst;
  }

  return stats;
}
