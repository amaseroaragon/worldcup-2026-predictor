import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { SectionCard } from "@/components/layout/section-card";
import { formatPercent } from "@/lib/formatters";
import type { WorldCupProbability } from "@/lib/types";

export function CompareTable({ probabilities }: { probabilities: WorldCupProbability[] }) {
  return (
    <SectionCard title="Model probabilities" description="Ranked by champion probability.">
      <div className="overflow-x-auto">
        <table className="w-full min-w-3xl text-left text-sm">
          <thead className="border-b text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="pb-3 pr-5 font-medium">Rank</th>
              <th className="pb-3 font-medium">Team</th>
              <th className="pb-3 font-medium">Champion</th>
              <th className="pb-3 font-medium">Runner-up</th>
              <th className="pb-3 text-right font-medium">Semi-final</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {probabilities.map((item, index) => (
              <tr key={item.team} className="transition hover:bg-muted/40">
                <td className="py-4 pr-5 font-bold text-muted-foreground">{index + 1}</td>
                <td className="py-4 pr-6 font-semibold">{item.team}</td>
                <td className="w-56 py-4 pr-8">
                  <div className="mb-2 font-semibold">{formatPercent(item.champion_probability, 1)}</div>
                  <ProbabilityBar value={item.champion_probability} />
                </td>
                <td className="py-4 pr-6">{formatPercent(item.runner_up_probability, 1)}</td>
                <td className="py-4 text-right">{formatPercent(item.semifinal_probability, 1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
