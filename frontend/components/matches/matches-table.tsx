import { TeamBadge } from "@/components/teams/team-badge";
import { formatPercent } from "@/lib/formatters";
import type { PredictedMatch } from "@/lib/types";
import { cn } from "@/lib/utils";

type MatchesTableProps = {
  matches: PredictedMatch[];
  compact?: boolean;
};

export function MatchesTable({ matches, compact = false }: MatchesTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-5xl text-left text-sm">
        <thead className="border-b text-xs uppercase tracking-wide text-muted-foreground">
          <tr>
            <th className="pb-3 font-medium">Round</th>
            <th className="pb-3 font-medium">Match</th>
            <th className="pb-3 font-medium">Team A</th>
            <th className="pb-3 font-medium">Team B</th>
            <th className="pb-3 font-medium">Prob A</th>
            <th className="pb-3 font-medium">Draw</th>
            <th className="pb-3 font-medium">Prob B</th>
            <th className="pb-3 text-right font-medium">Predicted result</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {matches.map((match) => (
            <tr key={match.id} className={cn("transition hover:bg-muted/40", compact ? "text-xs" : "text-sm")}>
              <td className="whitespace-nowrap py-4 pr-5 text-muted-foreground">{match.round}</td>
              <td className="py-4 pr-5 font-medium">#{match.matchNumber}</td>
              <td className="py-4 pr-6"><TeamBadge team={match.homeTeam} href={`/teams/${match.homeTeam.slug}`} /></td>
              <td className="py-4 pr-6"><TeamBadge team={match.awayTeam} href={`/teams/${match.awayTeam.slug}`} /></td>
              <td className="py-4 pr-5 font-semibold text-primary">{formatPercent(match.homeWinProbability)}</td>
              <td className="py-4 pr-5">{formatPercent(match.drawProbability)}</td>
              <td className="py-4 pr-5 font-semibold text-primary">{formatPercent(match.awayWinProbability)}</td>
              <td className="py-4 text-right">
                <span className="inline-flex min-w-14 justify-center rounded-lg bg-secondary px-3 py-1.5 font-bold">
                  {match.predictedHomeScore} - {match.predictedAwayScore}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
