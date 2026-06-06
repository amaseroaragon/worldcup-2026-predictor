import type { TournamentPredictionMatch } from "@/lib/types";

export const MATCH_ROUND_FILTERS = [
  "All",
  "Group Stage",
  "Round of 32",
  "Round of 16",
  "Quarter-final",
  "Semi-final",
  "Final",
] as const;

export type MatchRoundFilter = (typeof MATCH_ROUND_FILTERS)[number];

const ROUND_ORDER: Record<string, number> = {
  "Group Stage": 0,
  "Round of 32": 1,
  "Round of 16": 2,
  "Quarter-final": 3,
  "Semi-final": 4,
  "Third-place playoff": 5,
  Final: 6,
};

const normalizeKey = (value: string) =>
  value.toLowerCase().trim().replaceAll("-", "_").replaceAll(" ", "_");

export function formatMatchRound(match: Pick<TournamentPredictionMatch, "stage" | "round">): string {
  if (normalizeKey(match.stage) === "group") return "Group Stage";

  const key = normalizeKey(match.round ?? match.stage);
  const labels: Record<string, string> = {
    round_of_32: "Round of 32",
    round_of_16: "Round of 16",
    quarterfinal: "Quarter-final",
    quarter_final: "Quarter-final",
    semifinal: "Semi-final",
    semi_final: "Semi-final",
    third_place_playoff: "Third-place playoff",
    final: "Final",
  };

  return labels[key] ?? (match.round ?? match.stage);
}

export function formatMatchProbability(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";

  return new Intl.NumberFormat("en", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatPredictedScore(
  match: Pick<
    TournamentPredictionMatch,
    "predicted_home_goals" | "predicted_away_goals" | "most_common_score"
  >,
): string {
  if (
    match.predicted_home_goals !== null &&
    match.predicted_home_goals !== undefined &&
    match.predicted_away_goals !== null &&
    match.predicted_away_goals !== undefined
  ) {
    return `${match.predicted_home_goals}-${match.predicted_away_goals}`;
  }

  return match.most_common_score ?? "—";
}

export function sortMatchesByRound(
  matches: TournamentPredictionMatch[],
): TournamentPredictionMatch[] {
  return matches
    .map((match, index) => ({ match, index }))
    .toSorted((a, b) => {
      const roundDifference =
        (ROUND_ORDER[formatMatchRound(a.match)] ?? Number.MAX_SAFE_INTEGER) -
        (ROUND_ORDER[formatMatchRound(b.match)] ?? Number.MAX_SAFE_INTEGER);

      return roundDifference || a.index - b.index;
    })
    .map(({ match }) => match);
}
