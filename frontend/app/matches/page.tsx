import { PageContainer } from "@/components/layout/page-container";
import { MatchesExplorer } from "@/components/matches/matches-explorer";
import { loadTournamentPredictions } from "@/lib/data/load-prediction-data";

export const metadata = { title: "Matches" };

export default async function MatchesPage() {
  const { matches, metadata } = await loadTournamentPredictions();

  return (
    <PageContainer
      eyebrow="Fixture projections"
      title="Predicted matches"
      description="Browse projected fixtures, probabilities and expected results."
    >
      <p className="rounded-xl border border-dashed bg-card/60 px-4 py-3 text-sm text-muted-foreground">
        Loaded from the latest synchronized tournament predictions
        {typeof metadata.simulations === "number" ? ` · ${metadata.simulations.toLocaleString("en")} simulations` : ""}.
      </p>
      <MatchesExplorer matches={matches} />
    </PageContainer>
  );
}
