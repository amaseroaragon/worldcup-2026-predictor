import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { formatPercent } from "@/lib/formatters";
import type { WorldCupProbability } from "@/lib/types";

function ProbabilityCell({ value }: { value: number }) {
  return (
    <td className="w-64 px-6 py-5">
      <div className="mb-2 font-semibold">{formatPercent(value, 1)}</div>
      <ProbabilityBar value={value} />
    </td>
  );
}

export function CompareTable({ probabilities }: { probabilities: WorldCupProbability[] }) {
  return (
    <SectionCard title="Model probabilities" description="Ranked by champion probability.">
      <div className="overflow-x-auto">
        <table className="w-full min-w-5xl table-fixed text-left text-sm">
          <thead className="border-b text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="w-20 pb-3 pr-5 font-medium">Rank</th>
              <th className="w-56 pb-3 pr-8 font-medium">Team</th>
              <th className="w-64 px-6 pb-3 font-medium">Champion</th>
              <th className="w-64 px-6 pb-3 font-medium">Runner-up</th>
              <th className="w-64 px-6 pb-3 font-medium">Semi-final</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {probabilities.map((item, index) => (
              <tr key={item.team} className="transition hover:bg-muted/40">
                <td className="py-4 pr-5 font-bold text-muted-foreground">{index + 1}</td>
                <td className="py-5 pr-8"><TeamBadge team={item.team} size="sm" /></td>
                <ProbabilityCell value={item.champion_probability} />
                <ProbabilityCell value={item.runner_up_probability} />
                <ProbabilityCell value={item.semifinal_probability} />
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
