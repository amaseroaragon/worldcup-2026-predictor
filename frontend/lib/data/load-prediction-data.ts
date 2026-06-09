import type {
  GroupResults,
  TeamMetric,
  TeamProfile,
  RepresentativeTournament,
  TournamentPredictions,
  WorldCupProbability,
} from "@/lib/types";

import { loadPublicJson } from "./load-public-json";
import { getTeamRepresentativeSummary } from "./team-representative-summary";

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

export function loadRepresentativeTournament(): Promise<RepresentativeTournament> {
  return loadPublicJson("/data/representative_tournament.json");
}

export async function loadTeamProfiles(): Promise<TeamProfile[]> {
  const [{ teams }, probabilities, { groups }, representativeTournament] = await Promise.all([
    loadWorldCupTeamMetrics(),
    loadWorldCupProbabilities(),
    loadGroupResults(),
    loadRepresentativeTournament(),
  ]);
  const probabilitiesByTeam = new Map(probabilities.map((item) => [item.team, item]));
  const groupResultsByTeam = new Map(
    Object.values(groups).flatMap((standings) => standings.map((item) => [item.team, item] as const)),
  );

  return teams.map((metric) => ({
    metric,
    probability: probabilitiesByTeam.get(metric.team) ?? null,
    aggregateGroupResult: groupResultsByTeam.get(metric.team) ?? null,
    representativeSummary: getTeamRepresentativeSummary(metric.team, representativeTournament),
  }));
}
