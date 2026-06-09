import { BracketMatchCard } from "@/components/bracket/BracketMatchCard";
import type { BracketRoundLabel } from "@/lib/match-formatters";
import type { TournamentPredictionMatch } from "@/lib/types";

type BracketColumnProps = {
  round: BracketRoundLabel;
  matches: TournamentPredictionMatch[];
};

export function BracketColumn({ round, matches }: BracketColumnProps) {
  return (
    <section className="flex min-w-0 flex-col">
      <header className="mb-2 rounded-lg border bg-card/95 px-2.5 py-2 shadow-sm">
        <h2 className="text-xs font-bold tracking-tight">{round}</h2>
        <p className="mt-0.5 text-[0.65rem] text-muted-foreground">
          {matches.length} projected {matches.length === 1 ? "match" : "matches"}
        </p>
      </header>

      <div className="flex flex-1 flex-col justify-around gap-2">
        {matches.length > 0 ? (
          matches.map((match) => (
            <BracketMatchCard key={match.match_id} match={match} />
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
