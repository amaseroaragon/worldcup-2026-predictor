import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const rounds = ["All", "Group stage", "Round of 32", "Round of 16", "Quarter-final", "Semi-final", "Final"];

export function RoundFilters() {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1" aria-label="Match round filters">
      {rounds.map((round, index) => (
        <button
          key={round}
          type="button"
          aria-pressed={index === 0}
          className={cn(buttonVariants({ variant: index === 0 ? "default" : "outline" }), "shrink-0")}
        >
          {round}
        </button>
      ))}
    </div>
  );
}
