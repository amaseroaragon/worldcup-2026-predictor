import { GroupCard } from "@/components/groups/group-card";
import { PageContainer } from "@/components/layout/page-container";
import { loadGroupResults, loadTournamentPredictions } from "@/lib/data/load-prediction-data";
import { calculateProjectedGroupStats } from "@/lib/group-points";

export const metadata = { title: "Groups" };

export default async function GroupsPage() {
  const [{ groups, metadata }, { matches }] = await Promise.all([
    loadGroupResults(),
    loadTournamentPredictions(),
  ]);
  const groupEntries = Object.entries(groups).toSorted(([a], [b]) => a.localeCompare(b));
  const projectedStats = calculateProjectedGroupStats(matches);

  return (
    <PageContainer
      eyebrow="Group stage"
      title="Projected groups"
      description={`Aggregate group-stage projections from ${metadata.simulations?.toLocaleString("en") ?? "the latest"} Monte Carlo simulations.`}
    >
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {groupEntries.map(([group, teams]) => (
          <GroupCard key={group} group={group} teams={teams} projectedStats={projectedStats} />
        ))}
      </div>
    </PageContainer>
  );
}
