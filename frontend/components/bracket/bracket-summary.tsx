import { BracketColumn } from "@/components/bracket/BracketColumn";
import { positionBracketMatches, positionedRoundMatches } from "@/lib/bracket-layout";
import { BRACKET_ROUNDS, formatMatchRound } from "@/lib/match-formatters";
import type { RepresentativeBracketMatch } from "@/lib/types";

export function BracketSummary({ matches }: { matches: RepresentativeBracketMatch[] }) {
  const positions = positionBracketMatches(matches);
  const leafCount = matches.filter((match) => match.round === "round_of_32").length;

  return (
    <div className="-mx-4 overflow-x-auto px-4 pb-5 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
      <div className="grid min-w-[62rem] grid-cols-5 items-stretch gap-2 rounded-2xl border bg-card/40 p-3 shadow-sm lg:min-w-0">
        {BRACKET_ROUNDS.map((round) => {
          const roundMatches = matches.filter((match) => formatMatchRound(match) === round);

          return (
            <BracketColumn
              key={round}
              round={round}
              matches={positionedRoundMatches(roundMatches, positions)}
              leafCount={leafCount}
            />
          );
        })}
      </div>
    </div>
  );
}
