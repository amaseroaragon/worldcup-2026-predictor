import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { loadTeamProfiles } from "@/lib/data/load-prediction-data";

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
                .toSorted((a, b) => a.metric.team.localeCompare(b.metric.team))
                .map(({ metric }) => (
                  <div key={metric.team} className="rounded-xl border bg-background px-3 py-3">
                    <TeamBadge team={metric.team} />
                  </div>
                ))}
            </div>
          </SectionCard>
        ))}
      </div>
    </PageContainer>
  );
}
