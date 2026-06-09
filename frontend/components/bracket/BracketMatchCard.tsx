import { TeamBadge } from "@/components/teams/team-badge";
import { formatMatchProbability } from "@/lib/match-formatters";
import type { TournamentPredictionMatch } from "@/lib/types";
import { cn } from "@/lib/utils";

type BracketMatchCardProps = {
  match: TournamentPredictionMatch;
};

type TeamRowProps = {
  team: string;
  probability: number | null;
  goals: number | null;
  isWinner: boolean;
};

function TeamRow({ team, probability, goals, isWinner }: TeamRowProps) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto_auto] items-center gap-1.5">
      <TeamBadge
        team={team}
        size="sm"
        className="min-w-0 gap-1.5 text-xs"
        nameClassName={cn("truncate", isWinner ? "font-bold" : "font-normal")}
      />
      <span className="text-[0.7rem] font-semibold text-primary">
        {formatMatchProbability(probability)}
      </span>
      <span className={cn("w-3 text-right text-xs", isWinner ? "font-bold" : "font-normal")}>
        {goals ?? "—"}
      </span>
    </div>
  );
}

export function BracketMatchCard({ match }: BracketMatchCardProps) {
  return (
    <article className="rounded-lg border bg-background p-2.5 shadow-sm">
      <div className="space-y-1.5">
        <TeamRow
          team={match.home_team}
          probability={match.home_win_probability}
          goals={match.predicted_home_goals}
          isWinner={match.predicted_winner === match.home_team}
        />
        <TeamRow
          team={match.away_team}
          probability={match.away_win_probability}
          goals={match.predicted_away_goals}
          isWinner={match.predicted_winner === match.away_team}
        />
      </div>
    </article>
  );
}
