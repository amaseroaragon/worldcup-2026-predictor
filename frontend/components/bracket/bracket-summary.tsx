import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import {
  BRACKET_ROUNDS,
  formatMatchProbability,
  formatMatchRound,
  formatPredictedScore,
} from "@/lib/match-formatters";
import type { TournamentPredictionMatch } from "@/lib/types";

function MatchCard({ match }: { match: TournamentPredictionMatch }) {
  return (
    <article className="rounded-xl border bg-background p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <span className="text-xs font-semibold text-muted-foreground">{match.match_id}</span>
        <span className="rounded-md bg-secondary px-2 py-1 text-xs font-bold">
          {formatPredictedScore(match)}
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3">
          <TeamBadge team={match.home_team} size="sm" />
          <span className="text-sm font-bold text-primary">
            {formatMatchProbability(match.home_win_probability)}
          </span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <TeamBadge team={match.away_team} size="sm" />
          <span className="text-sm font-bold text-primary">
            {formatMatchProbability(match.away_win_probability)}
          </span>
        </div>
      </div>

      <div className="mt-4 space-y-1 border-t pt-3 text-xs text-muted-foreground">
        {match.draw_probability !== null && match.draw_probability !== undefined && (
          <div className="flex justify-between gap-3">
            <span>Draw</span>
            <span>{formatMatchProbability(match.draw_probability)}</span>
          </div>
        )}
        <div className="flex justify-between gap-3">
          <span>Winner</span>
          {match.predicted_winner ? (
            <TeamBadge team={match.predicted_winner} size="sm" />
          ) : (
            <span>—</span>
          )}
        </div>
        <div className="flex justify-between gap-3">
          <span>Appearance</span>
          <span>{formatMatchProbability(match.appearance_probability)}</span>
        </div>
      </div>
    </article>
  );
}

export function BracketSummary({ matches }: { matches: TournamentPredictionMatch[] }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
      {BRACKET_ROUNDS.map((round) => {
        const roundMatches = matches.filter((match) => formatMatchRound(match) === round);

        return (
          <SectionCard key={round} title={round} className="min-w-0">
            {roundMatches.length > 0 ? (
              <div className="space-y-3">
                {roundMatches.map((match) => <MatchCard key={match.match_id} match={match} />)}
              </div>
            ) : (
              <p className="rounded-xl bg-muted/60 px-4 py-8 text-center text-sm text-muted-foreground">
                No projected matches available for this round yet.
              </p>
            )}
          </SectionCard>
        );
      })}
    </div>
  );
}
