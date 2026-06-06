import type {
  GroupResults,
  TeamMetric,
  TournamentPredictions,
  WorldCupProbability,
} from "@/lib/types";

import { loadPublicJson } from "./load-public-json";

type TeamMetricsPayload = {
  metadata: { source: string; scope: string };
  teams: TeamMetric[];
};

export function loadWorldCupProbabilities(): Promise<WorldCupProbability[]> {
  return loadPublicJson("/data/world_cup_probabilities.json");
}

export function loadWorldCupTeamMetrics(): Promise<TeamMetricsPayload> {
  return loadPublicJson("/data/world_cup_team_metrics.json");
}

export function loadGroupResults(): Promise<GroupResults> {
  return loadPublicJson("/data/group_results.json");
}

export function loadTournamentPredictions(): Promise<TournamentPredictions> {
  return loadPublicJson("/data/tournament_predictions.json");
}
