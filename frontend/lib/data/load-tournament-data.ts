import type { TournamentData } from "@/lib/types";

import { mockBracket, mockGroups, mockMatches, mockProbabilities } from "./mock-data";

/**
 * Data access boundary for the frontend.
 *
 * Replace the mock return value with validated imports or reads from
 * `public/data/` when the Python JSON export contract is finalized.
 */
export async function loadTournamentData(): Promise<TournamentData> {
  return {
    groups: mockGroups,
    bracket: mockBracket,
    matches: mockMatches,
    probabilities: mockProbabilities,
  };
}
