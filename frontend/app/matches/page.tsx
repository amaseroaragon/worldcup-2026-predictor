import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { MatchesTable } from "@/components/matches/matches-table";
import { RoundFilters } from "@/components/matches/round-filters";
import { loadTournamentData } from "@/lib/data/load-tournament-data";

export const metadata = { title: "Matches" };

export default async function MatchesPage() {
  const { matches } = await loadTournamentData();

  return (
    <PageContainer
      eyebrow="Fixture projections"
      title="Predicted matches"
      description="Browse projected fixtures, probabilities and expected results."
    >
      <p className="rounded-xl border border-dashed bg-card/60 px-4 py-3 text-sm text-muted-foreground">
        Mock data until Python-generated JSON is connected.
      </p>
      <RoundFilters />
      <SectionCard title="Projected fixtures" description="Filters are visual placeholders in this first iteration.">
        <MatchesTable matches={matches} />
      </SectionCard>
    </PageContainer>
  );
}
