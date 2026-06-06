import { notFound } from "next/navigation";

import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { loadTournamentData } from "@/lib/data/load-tournament-data";
import { formatPercent } from "@/lib/formatters";

type TeamPageProps = { params: Promise<{ team: string }> };

export default async function TeamPage({ params }: TeamPageProps) {
  const { team: slug } = await params;
  const { probabilities } = await loadTournamentData();
  const prediction = probabilities.find((item) => item.team.slug === slug);

  if (!prediction) notFound();

  const stages = [
    ["Reach round of 16", prediction.reachRoundOf16],
    ["Reach quarter-finals", prediction.reachQuarterFinal],
    ["Reach semi-finals", prediction.reachSemiFinal],
    ["Reach final", prediction.reachFinal],
    ["Win tournament", prediction.winTournament],
  ] as const;

  return (
    <PageContainer
      eyebrow={`Team profile · Group ${prediction.team.group}`}
      title={prediction.team.name}
      description="Mock data until Python-generated JSON is connected."
    >
      <SectionCard title="Tournament probabilities">
        <div className="mb-7">
          <TeamBadge team={prediction.team} size="lg" />
        </div>
        <div className="space-y-5">
          {stages.map(([label, value]) => (
            <div key={label}>
              <div className="mb-2 flex justify-between text-sm">
                <span className="font-medium">{label}</span>
                <span className="font-semibold">{formatPercent(value)}</span>
              </div>
              <ProbabilityBar value={value} />
            </div>
          ))}
        </div>
      </SectionCard>
    </PageContainer>
  );
}
