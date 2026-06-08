import type { TournamentPredictionMatch } from "@/lib/types";

export function calculateProjectedGroupPoints(
  matches: TournamentPredictionMatch[],
): Record<string, number> {
  const points: Record<string, number> = {};

  for (const match of matches) {
    if (match.stage !== "group") continue;

    points[match.home_team] ??= 0;
    points[match.away_team] ??= 0;

    if (match.predicted_home_goals === null || match.predicted_away_goals === null) continue;

    if (match.predicted_home_goals > match.predicted_away_goals) {
      points[match.home_team] += 3;
    } else if (match.predicted_home_goals < match.predicted_away_goals) {
      points[match.away_team] += 3;
    } else {
      points[match.home_team] += 1;
      points[match.away_team] += 1;
    }
  }

  return points;
}
