import type { ActualGroupMatch, ActualKnockoutMatch, ActualStage } from "@/lib/types";

export const STAGES: ActualStage[] = [
  "group",
  "round_of_32",
  "round_of_16",
  "quarter_final",
  "semi_final",
  "final",
  "champion",
];

export function stageIndex(stage: ActualStage): number {
  return STAGES.indexOf(stage);
}

export function reachedAtLeast(actual: ActualStage, stage: ActualStage): boolean {
  return stageIndex(actual) >= stageIndex(stage);
}

/** Round key used in the bracket JSON → the stage a team reaches by playing in it. */
export function roundToStage(round: string): ActualStage {
  if (round === "third_place_playoff") return "semi_final";
  return round as ActualStage;
}

export type ActualGroupRow = { team: string; played: number; points: number; goalsFor: number; goalsAgainst: number };

/** Points and goals per team from the real group matches (display only; qualification comes from actual stages). */
export function actualGroupRows(matches: ActualGroupMatch[]): Map<string, ActualGroupRow> {
  const rows = new Map<string, ActualGroupRow>();
  const row = (team: string) => {
    let current = rows.get(team);
    if (!current) {
      current = { team, played: 0, points: 0, goalsFor: 0, goalsAgainst: 0 };
      rows.set(team, current);
    }
    return current;
  };

  for (const match of matches) {
    const home = row(match.home_team);
    const away = row(match.away_team);
    home.played += 1;
    away.played += 1;
    home.goalsFor += match.home_score;
    home.goalsAgainst += match.away_score;
    away.goalsFor += match.away_score;
    away.goalsAgainst += match.home_score;
    if (match.outcome === "home") home.points += 3;
    else if (match.outcome === "away") away.points += 3;
    else {
      home.points += 1;
      away.points += 1;
    }
  }
  return rows;
}

export type TreeMatch = {
  match_id: string;
  round: string;
  source_match_ids: string[];
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  winner: string;
};

/** Rebuilds the real bracket tree: each match's sources are the previous-round matches its teams won. */
export function actualBracketTree(matches: ActualKnockoutMatch[]): Array<TreeMatch & { source: ActualKnockoutMatch }> {
  const order = ["round_of_32", "round_of_16", "quarter_final", "semi_final", "final"];
  const tree = matches
    .filter((match) => order.includes(match.stage))
    .map((match) => ({
      match_id: `A${match.match_number}`,
      round: match.stage,
      source_match_ids: [] as string[],
      home_team: match.home_team,
      away_team: match.away_team,
      home_score: match.home_score,
      away_score: match.away_score,
      winner: match.winner,
      source: match,
    }));

  for (const match of tree) {
    const previous = order[order.indexOf(match.round) - 1];
    if (!previous) continue;
    match.source_match_ids = [match.home_team, match.away_team]
      .map((team) => tree.find((candidate) => candidate.round === previous && candidate.winner === team)?.match_id)
      .filter((id): id is string => Boolean(id));
  }
  return tree;
}
