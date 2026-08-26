import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { loadTeamProfiles } from "@/lib/data/load-prediction-data";
import { formatOptionalNumber, formatOptionalPercent } from "@/lib/formatters";

export const metadata = { title: "Teams" };

export default async function TeamsPage() {
  const profiles = await loadTeamProfiles();
  const groups = profiles.reduce<Record<string, typeof profiles>>((result, profile) => {
    const group = profile.metric.group;
    result[group] ??= [];
    result[group].push(profile);
    return result;
  }, {});
  const groupEntries = Object.entries(groups).toSorted(([a], [b]) => a.localeCompare(b));

  return (
    <PageContainer
      eyebrow="Team profiles"
      title="Teams"
      description="Explore model metrics, group projections and tournament probabilities for every team."
    >
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {groupEntries.map(([group, teams]) => (
          <SectionCard key={group} title={`Group ${group}`}>
            <div className="grid gap-2">
              {teams
                .toSorted(
                  (a, b) =>
                    a.predictionSummary.group_position - b.predictionSummary.group_position ||
                    a.metric.team.localeCompare(b.metric.team),
                )
                .map(({ metric, aggregateGroupResult, predictionSummary }) => (
                  <div key={metric.team} className="rounded-xl border bg-background px-3 py-3">
                    <TeamBadge team={metric.team} />
                    <dl className="mt-3 grid grid-cols-3 gap-2 border-t pt-3 text-xs">
                      <div>
                        <dt className="text-muted-foreground">Group</dt>
                        <dd className="mt-1 font-semibold">{metric.group}</dd>
                      </div>
                      <div>
                        <dt className="text-muted-foreground">Projected position</dt>
                        <dd className="mt-1 font-semibold">
                          {formatOptionalNumber(predictionSummary.group_position, 0)}
                        </dd>
                      </div>
                      <div className="text-right">
                        <dt className="text-muted-foreground">Qualification</dt>
                        <dd className="mt-1 font-semibold text-primary">
                          {formatOptionalPercent(aggregateGroupResult?.qualification_probability)}
                        </dd>
                      </div>
                    </dl>
                  </div>
                ))}
            </div>
          </SectionCard>
        ))}
      </div>
    </PageContainer>
  );
}
