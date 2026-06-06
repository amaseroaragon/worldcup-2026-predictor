import { buttonVariants } from "@/components/ui/button";
import { MATCH_ROUND_FILTERS, type MatchRoundFilter } from "@/lib/match-formatters";
import { cn } from "@/lib/utils";

type RoundFiltersProps = {
  selectedRound: MatchRoundFilter;
  onSelectRound: (round: MatchRoundFilter) => void;
};

export function RoundFilters({ selectedRound, onSelectRound }: RoundFiltersProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1" aria-label="Match round filters">
      {MATCH_ROUND_FILTERS.map((round) => (
        <button
          key={round}
          type="button"
          aria-pressed={selectedRound === round}
          onClick={() => onSelectRound(round)}
          className={cn(buttonVariants({ variant: selectedRound === round ? "default" : "outline" }), "shrink-0")}
        >
          {round}
        </button>
      ))}
    </div>
  );
}
