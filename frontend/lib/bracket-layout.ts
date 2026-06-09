import type { RepresentativeBracketMatch } from "@/lib/types";

export type PositionedBracketMatch = {
  match: RepresentativeBracketMatch;
  position: number;
};

function numericMatchId(matchId: string): number {
  return Number(matchId.replace(/\D/g, ""));
}

export function positionBracketMatches(
  matches: RepresentativeBracketMatch[],
): Map<string, number> {
  const matchesById = new Map(matches.map((match) => [match.match_id, match]));
  const final = matches.find((match) => match.round === "final");

  if (!final) return new Map();

  const positionById = new Map<string, number>();
  const subtreeOrderById = new Map<string, number>();
  const visiting = new Set<string>();

  function subtreeOrder(matchId: string): number {
    const existing = subtreeOrderById.get(matchId);
    if (existing !== undefined) return existing;

    const match = matchesById.get(matchId);
    if (!match) return numericMatchId(matchId);

    const sourceIds = match.source_match_ids.filter((sourceId) => matchesById.has(sourceId));
    const order =
      sourceIds.length === 0
        ? numericMatchId(matchId)
        : Math.min(...sourceIds.map((sourceId) => subtreeOrder(sourceId)));
    subtreeOrderById.set(matchId, order);
    return order;
  }

  function placeSources(matchId: string, nextLeafPosition: { value: number }): number {
    const existing = positionById.get(matchId);
    if (existing !== undefined) return existing;

    if (visiting.has(matchId)) {
      throw new Error(`Circular bracket source detected at ${matchId}`);
    }

    const match = matchesById.get(matchId);
    if (!match) {
      throw new Error(`Bracket source ${matchId} does not exist`);
    }

    visiting.add(matchId);
    const sourceIds = match.source_match_ids
      .filter((sourceId) => matchesById.has(sourceId))
      .toSorted((a, b) => subtreeOrder(a) - subtreeOrder(b));
    const position =
      sourceIds.length === 0
        ? nextLeafPosition.value++
        : sourceIds
            .map((sourceId) => placeSources(sourceId, nextLeafPosition))
            .reduce((total, sourcePosition) => total + sourcePosition, 0) / sourceIds.length;

    visiting.delete(matchId);
    positionById.set(matchId, position);
    return position;
  }

  placeSources(final.match_id, { value: 0 });

  const disconnected = matches
    .filter((match) => !positionById.has(match.match_id))
    .toSorted((a, b) => numericMatchId(a.match_id) - numericMatchId(b.match_id));
  const nextLeafPosition = { value: positionById.size };
  disconnected.forEach((match) => placeSources(match.match_id, nextLeafPosition));

  return positionById;
}

export function positionedRoundMatches(
  matches: RepresentativeBracketMatch[],
  positions: Map<string, number>,
): PositionedBracketMatch[] {
  return matches
    .map((match) => ({
      match,
      position: positions.get(match.match_id) ?? Number.MAX_SAFE_INTEGER,
    }))
    .toSorted((a, b) => a.position - b.position);
}
