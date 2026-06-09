import { BracketColumn } from "@/components/bracket/BracketColumn";
import { BRACKET_ROUNDS, formatMatchRound } from "@/lib/match-formatters";
import type { TournamentPredictionMatch } from "@/lib/types";

export function BracketSummary({ matches }: { matches: TournamentPredictionMatch[] }) {
  return (
    <div className="-mx-4 overflow-x-auto px-4 pb-5 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
      <div className="grid min-w-[62rem] grid-cols-5 items-stretch gap-2 rounded-2xl border bg-card/40 p-3 shadow-sm lg:min-w-0">
        {BRACKET_ROUNDS.map((round) => (
          <BracketColumn
            key={round}
            round={round}
            matches={matches.filter((match) => formatMatchRound(match) === round)}
          />
        ))}
      </div>
    </div>
  );
}
