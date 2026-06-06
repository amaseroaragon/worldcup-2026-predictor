import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { formatPercent } from "@/lib/formatters";
import type { TournamentProbabilities } from "@/lib/types";

export function CompareTable({ probabilities }: { probabilities: TournamentProbabilities[] }) {
  return (
    <SectionCard title="Probability comparison" description="Mock data until Python-generated JSON is connected.">
      <div className="overflow-x-auto">
        <table className="w-full min-w-3xl text-left text-sm">
          <thead className="border-b text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="pb-3 font-medium">Team</th>
              <th className="pb-3 font-medium">Round of 16</th>
              <th className="pb-3 font-medium">Semi-final</th>
              <th className="pb-3 font-medium">Final</th>
              <th className="pb-3 font-medium">Champion</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {probabilities.map((item) => (
              <tr key={item.team.id}>
                <td className="py-4 pr-6"><TeamBadge team={item.team} href={`/teams/${item.team.slug}`} /></td>
                <td className="py-4 pr-6">{formatPercent(item.reachRoundOf16)}</td>
                <td className="py-4 pr-6">{formatPercent(item.reachSemiFinal)}</td>
                <td className="py-4 pr-6">{formatPercent(item.reachFinal)}</td>
                <td className="w-48 py-4">
                  <div className="mb-2 font-semibold">{formatPercent(item.winTournament)}</div>
                  <ProbabilityBar value={item.winTournament} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
