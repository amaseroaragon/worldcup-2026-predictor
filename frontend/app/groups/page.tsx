import { GroupCard } from "@/components/groups/group-card";
import { PageContainer } from "@/components/layout/page-container";
import { loadGroupResults } from "@/lib/data/load-prediction-data";

export const metadata = { title: "Groups" };

export default async function GroupsPage() {
  const { groups, metadata } = await loadGroupResults();
  const groupEntries = Object.entries(groups).toSorted(([a], [b]) => a.localeCompare(b));

  return (
    <PageContainer
      eyebrow="Group stage"
      title="Projected groups"
      description={`Aggregate group-stage projections from ${metadata.simulations?.toLocaleString("en") ?? "the latest"} Monte Carlo simulations.`}
    >
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {groupEntries.map(([group, teams]) => <GroupCard key={group} group={group} teams={teams} />)}
      </div>
    </PageContainer>
  );
}
