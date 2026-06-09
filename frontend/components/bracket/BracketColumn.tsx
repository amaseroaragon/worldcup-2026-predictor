import { BracketMatchCard } from "@/components/bracket/BracketMatchCard";
import type { PositionedBracketMatch } from "@/lib/bracket-layout";
import type { BracketRoundLabel } from "@/lib/match-formatters";

type BracketColumnProps = {
  round: BracketRoundLabel;
  matches: PositionedBracketMatch[];
  leafCount: number;
};

export function BracketColumn({ round, matches, leafCount }: BracketColumnProps) {
  return (
    <section className="flex min-w-0 flex-col">
      <header className="mb-2 rounded-lg border bg-card/95 px-2.5 py-2 shadow-sm">
        <h2 className="text-xs font-bold tracking-tight">{round}</h2>
        <p className="mt-0.5 text-[0.65rem] text-muted-foreground">
          {matches.length} projected {matches.length === 1 ? "match" : "matches"}
        </p>
      </header>

      <div className="relative h-[160rem]">
        {matches.length > 0 ? (
          matches.map(({ match, position }) => (
            <div
              key={match.match_id}
              className="absolute inset-x-0 -translate-y-1/2"
              style={{ top: `${((position + 0.5) / leafCount) * 100}%` }}
            >
              <BracketMatchCard match={match} />
            </div>
          ))
        ) : (
          <p className="rounded-xl border border-dashed bg-muted/40 px-4 py-8 text-center text-sm text-muted-foreground">
            No projected matches available yet.
          </p>
        )}
      </div>
    </section>
  );
}
