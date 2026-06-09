import { formatMatchRound } from "@/lib/match-formatters";
import type {
  RepresentativeTournament,
  TeamPredictionSummary,
  TournamentPredictionMatch,
} from "@/lib/types";

const STAGE_ORDER: Record<string, number> = {
  "Group Stage": 0,
  "Round of 32": 1,
  "Round of 16": 2,
  "Quarter-final": 3,
  "Semi-final": 4,
  "Third-place playoff": 4,
  Final: 5,
};

function includesTeam(match: TournamentPredictionMatch, teamName: string): boolean {
  return match.home_team === teamName || match.away_team === teamName;
}

export function getTeamPredictionSummary(
  teamName: string,
  payload: RepresentativeTournament,
): TeamPredictionSummary {
  const representative = payload.representative_tournament;
  const standing = Object.values(representative.groups)
    .flat()
    .find((row) => row.team === teamName);

  if (!standing) {
    throw new Error(`Representative group standing not found for ${teamName}`);
  }

  const displayedMatches = representative.results.filter((match) =>
    includesTeam(match, teamName),
  );
  const knockoutMatches = representative.bracket.filter((match) =>
    includesTeam(match, teamName),
  );
  const furthestMatch = knockoutMatches.toSorted(
    (a, b) => (STAGE_ORDER[formatMatchRound(b)] ?? 0) - (STAGE_ORDER[formatMatchRound(a)] ?? 0),
  )[0];

  let stageReached = furthestMatch ? formatMatchRound(furthestMatch) : "Group Stage";
  if (stageReached === "Third-place playoff") stageReached = "Semi-final";
  if (representative.champion === teamName) stageReached = "Champion";

  return {
    group_position: standing.position,
    points: standing.points,
    goals_for: standing.goals_for,
    goals_against: standing.goals_against,
    goal_difference: standing.goal_difference,
    qualified: representative.qualified.round_of_32.includes(teamName),
    stage_reached: stageReached,
    displayed_matches: displayedMatches,
  };
}
