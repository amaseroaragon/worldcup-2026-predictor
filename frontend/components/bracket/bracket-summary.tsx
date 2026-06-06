import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import type { Bracket } from "@/lib/types";

export function BracketSummary({ bracket }: { bracket: Bracket }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
      {bracket.rounds.map((round) => (
        <SectionCard key={round.name} title={round.name}>
          <div className="space-y-3">
            {round.matches.map((match) => (
              <div key={match.id} className="rounded-xl bg-muted/60 p-3">
                <div className="space-y-2">
                  <TeamBadge team={match.homeTeam} href={`/teams/${match.homeTeam.slug}`} />
                  <TeamBadge team={match.awayTeam} href={`/teams/${match.awayTeam.slug}`} />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      ))}
    </div>
  );
}
