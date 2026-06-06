import {
  formatMatchProbability,
  formatMatchRound,
  formatPredictedScore,
} from "@/lib/match-formatters";
import type { TournamentPredictionMatch } from "@/lib/types";

type MatchesTableProps = {
  matches: TournamentPredictionMatch[];
};

export function MatchesTable({ matches }: MatchesTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-7xl text-left text-sm">
        <thead className="border-b text-xs uppercase tracking-wide text-muted-foreground">
          <tr>
            <th className="pb-3 font-medium">Round</th>
            <th className="pb-3 font-medium">Match</th>
            <th className="pb-3 font-medium">Team A</th>
            <th className="pb-3 font-medium">Team B</th>
            <th className="pb-3 font-medium">Prob A</th>
            <th className="pb-3 font-medium">Draw</th>
            <th className="pb-3 font-medium">Prob B</th>
            <th className="pb-3 font-medium">Predicted score</th>
            <th className="pb-3 font-medium">Predicted winner</th>
            <th className="pb-3 text-right font-medium">Appearance</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {matches.map((match) => (
            <tr key={match.match_id} className="transition hover:bg-muted/40">
              <td className="whitespace-nowrap py-4 pr-5 text-muted-foreground">{formatMatchRound(match)}</td>
              <td className="whitespace-nowrap py-4 pr-5 font-medium">{match.match_id}</td>
              <td className="whitespace-nowrap py-4 pr-6 font-semibold">{match.home_team}</td>
              <td className="whitespace-nowrap py-4 pr-6 font-semibold">{match.away_team}</td>
              <td className="py-4 pr-5 font-semibold text-primary">{formatMatchProbability(match.home_win_probability)}</td>
              <td className="py-4 pr-5">{formatMatchProbability(match.draw_probability)}</td>
              <td className="py-4 pr-5 font-semibold text-primary">{formatMatchProbability(match.away_win_probability)}</td>
              <td className="py-4 pr-5">
                <span className="inline-flex min-w-14 justify-center rounded-lg bg-secondary px-3 py-1.5 font-bold">
                  {formatPredictedScore(match)}
                </span>
              </td>
              <td className="whitespace-nowrap py-4 pr-5">{match.predicted_winner ?? "—"}</td>
              <td className="py-4 text-right">{formatMatchProbability(match.appearance_probability)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
