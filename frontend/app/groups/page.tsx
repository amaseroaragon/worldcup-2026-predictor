import { GroupCard } from "@/components/groups/group-card";
import { PageContainer } from "@/components/layout/page-container";
import { loadTournamentData } from "@/lib/data/load-tournament-data";

export const metadata = { title: "Groups" };

export default async function GroupsPage() {
  const { groups } = await loadTournamentData();

  return (
    <PageContainer
      eyebrow="Group stage"
      title="Projected groups"
      description="Mock group composition until Python-generated JSON is connected."
    >
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {groups.map((group) => <GroupCard key={group.id} group={group} />)}
      </div>
    </PageContainer>
  );
}
