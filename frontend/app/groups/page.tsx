import { GroupCard } from "@/components/groups/group-card";
import { PageContainer } from "@/components/layout/page-container";
import { loadRepresentativeTournament } from "@/lib/data/load-prediction-data";

export const metadata = { title: "Groups" };

export default async function GroupsPage() {
  const { metadata, representative_tournament } = await loadRepresentativeTournament();
  const { groups } = representative_tournament;
  const groupEntries = Object.entries(groups).toSorted(([a], [b]) => a.localeCompare(b));

  return (
    <PageContainer
      eyebrow="Group stage"
      title="Projected groups"
      description={`One coherent deterministic prediction derived from ${
        typeof metadata.simulations === "number"
          ? `${metadata.simulations.toLocaleString("en")} Monte Carlo simulations`
          : "the latest model run"
      }.`}
    >
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {groupEntries.map(([group, teams]) => (
          <GroupCard key={group} group={group} teams={teams} />
        ))}
      </div>
    </PageContainer>
  );
}
