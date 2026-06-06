"use client";

import { useMemo, useState } from "react";

import { SectionCard } from "@/components/layout/section-card";
import { MatchesTable } from "@/components/matches/matches-table";
import { RoundFilters } from "@/components/matches/round-filters";
import {
  formatMatchRound,
  sortMatchesByRound,
  type MatchRoundFilter,
} from "@/lib/match-formatters";
import type { TournamentPredictionMatch } from "@/lib/types";

export function MatchesExplorer({ matches }: { matches: TournamentPredictionMatch[] }) {
  const [selectedRound, setSelectedRound] = useState<MatchRoundFilter>("All");
  const sortedMatches = useMemo(() => sortMatchesByRound(matches), [matches]);
  const visibleMatches = useMemo(
    () =>
      selectedRound === "All"
        ? sortedMatches
        : sortedMatches.filter((match) => formatMatchRound(match) === selectedRound),
    [selectedRound, sortedMatches],
  );

  return (
    <>
      <RoundFilters selectedRound={selectedRound} onSelectRound={setSelectedRound} />
      <SectionCard
        title="Projected fixtures"
        description={`${visibleMatches.length} match${visibleMatches.length === 1 ? "" : "es"} shown`}
      >
        {visibleMatches.length > 0 ? (
          <MatchesTable matches={visibleMatches} />
        ) : (
          <p className="rounded-xl bg-muted/60 px-4 py-8 text-center text-sm text-muted-foreground">
            No matches available for this round yet.
          </p>
        )}
      </SectionCard>
    </>
  );
}
