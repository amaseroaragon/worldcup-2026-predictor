import { CompareTable } from "@/components/compare/compare-table";
import { PageContainer } from "@/components/layout/page-container";
import { loadTournamentData } from "@/lib/data/load-tournament-data";

export const metadata = { title: "Compare" };

export default async function ComparePage() {
  const { probabilities } = await loadTournamentData();

  return (
    <PageContainer
      eyebrow="Team analysis"
      title="Compare contenders"
      description="Mock probability comparison until Python-generated JSON is connected."
    >
      <CompareTable probabilities={probabilities} />
    </PageContainer>
  );
}
