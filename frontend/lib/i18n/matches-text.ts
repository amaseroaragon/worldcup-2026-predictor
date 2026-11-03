import type { MatchesText } from "@/components/matches/matches-explorer";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import type { EloRatings } from "@/lib/types";

/** Serialisable text bundle for the client-side match list. */
export function buildMatchesText(t: Dictionary, elo: EloRatings): MatchesText {
  return {
    ui: t.matchesUi,
    outcome: t.outcome,
    rounds: t.rounds,
    groupLabelByTeam: Object.fromEntries(elo.teams.map((row) => [row.team, t.common.group(row.group)])),
    penalties: t.common.onPenalties("{team}"),
  };
}
