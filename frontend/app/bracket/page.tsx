import { BracketSummary } from "@/components/bracket/bracket-summary";
import { PageContainer } from "@/components/layout/page-container";
import { loadTournamentData } from "@/lib/data/load-tournament-data";

export const metadata = { title: "Bracket" };

export default async function BracketPage() {
  const { bracket } = await loadTournamentData();

  return (
    <PageContainer
      eyebrow="Knockout stage"
      title="Most likely bracket"
      description="A placeholder bracket ready to receive simulated knockout matchups."
    >
      <BracketSummary bracket={bracket} />
    </PageContainer>
  );
}
