import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { notFound } from "next/navigation";

import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { buttonVariants } from "@/components/ui/button";
import { loadTeamProfiles } from "@/lib/data/load-prediction-data";
import {
  formatOptionalNumber,
  formatOptionalPercent,
} from "@/lib/formatters";
import { teamNameToSlug } from "@/lib/team-slugs";
import { cn } from "@/lib/utils";

type TeamPageProps = { params: Promise<{ team: string }> };

export async function generateStaticParams() {
  const profiles = await loadTeamProfiles();
  return profiles.map(({ metric }) => ({ team: teamNameToSlug(metric.team) }));
}

export default async function TeamPage({ params }: TeamPageProps) {
  const { team: slug } = await params;
  const profiles = await loadTeamProfiles();
  const profile = profiles.find(({ metric }) => teamNameToSlug(metric.team) === slug);

  if (!profile) notFound();

  const { metric, probability, aggregateGroupResult, representativeSummary } = profile;
  const probabilities = [
    ["Qualification probability", aggregateGroupResult?.qualification_probability],
    ["Champion probability", probability?.champion_probability],
    ["Runner-up probability", probability?.runner_up_probability],
    ["Semi-final probability", probability?.semifinal_probability],
  ] as const;
  const metrics = [
    ["Elo", metric.elo],
    ["Attack Rating", metric.attack_rating],
    ["Defense Rating", metric.defense_rating],
    ["Recent Form (5)", metric.recent_form?.form_5],
    ["Recent Form (10)", metric.recent_form?.form_10],
    ["Recent Form (20)", metric.recent_form?.form_20],
    ["Squad Strength", metric.squad_strength?.squad_strength_rating],
    ["Matches Used", metric.matches_used],
  ] as const;

  return (
    <PageContainer
      eyebrow={`Team profile · Group ${metric.group}`}
      title={metric.team}
      description="Representative tournament outcome, aggregate Monte Carlo probabilities and model metrics."
    >
      <Link href="/groups" className={cn(buttonVariants({ variant: "outline" }), "w-fit")}>
        <ArrowLeft /> Back
      </Link>

      <SectionCard title="National team">
        <TeamBadge team={metric.team} size="lg" linked={false} />
        <p className="mt-4 text-sm text-muted-foreground">Group {metric.group}</p>
      </SectionCard>

      <SectionCard
        title="Representative scenario"
        description="Results from the same coherent tournament scenario shown in Groups and Bracket."
      >
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Predicted group position" value={formatOptionalNumber(representativeSummary.group_position, 0)} />
          <Metric label="Points" value={formatOptionalNumber(representativeSummary.points, 0)} />
          <Metric label="Goals for" value={formatOptionalNumber(representativeSummary.goals_for, 0)} />
          <Metric label="Goals against" value={formatOptionalNumber(representativeSummary.goals_against, 0)} />
          <Metric label="Goal difference" value={formatOptionalNumber(representativeSummary.goal_difference, 0)} />
          <Metric label="Group status" value={representativeSummary.qualified ? "Qualified" : "Eliminated"} />
          <Metric label="Stage reached" value={representativeSummary.stage_reached} />
          <Metric label="Matches played" value={formatOptionalNumber(representativeSummary.representative_matches.length, 0)} />
        </dl>
      </SectionCard>

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard
          title="Monte Carlo probabilities"
          description="Aggregate outcomes across all simulations."
        >
          <div className="space-y-5">
            {probabilities.map(([label, value]) => (
              <div key={label}>
                <div className="mb-2 flex justify-between gap-4 text-sm">
                  <span className="font-medium">{label}</span>
                  <span className="font-semibold">{formatOptionalPercent(value, 1)}</span>
                </div>
                {value !== null && value !== undefined && <ProbabilityBar value={value} />}
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="Monte Carlo group averages"
          description="Expected values across all simulations, not the representative scenario."
        >
          <dl className="grid grid-cols-2 gap-4">
            <Metric label="Expected group position" value={formatOptionalNumber(aggregateGroupResult?.expected_position)} />
            <Metric label="Expected points" value={formatOptionalNumber(aggregateGroupResult?.expected_points)} />
            <Metric label="Expected goals for" value={formatOptionalNumber(aggregateGroupResult?.expected_goals_for)} />
            <Metric label="Expected goals against" value={formatOptionalNumber(aggregateGroupResult?.expected_goals_against)} />
          </dl>
        </SectionCard>
      </div>

      <SectionCard title="Model metrics" description="Structural team inputs used by the prediction model.">
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(([label, value]) => (
            <Metric
              key={label}
              label={label}
              value={formatOptionalNumber(value, label === "Matches Used" ? 0 : 2)}
            />
          ))}
        </dl>
      </SectionCard>
    </PageContainer>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-muted/60 p-4">
      <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="mt-2 text-xl font-bold">{value}</dd>
    </div>
  );
}
