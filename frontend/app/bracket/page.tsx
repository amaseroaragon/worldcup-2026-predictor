import { BracketSummary } from "@/components/bracket/bracket-summary";
import { PageContainer } from "@/components/layout/page-container";
import { loadTournamentPredictions } from "@/lib/data/load-prediction-data";

export const metadata = { title: "Bracket" };

export default async function BracketPage() {
  const { matches, metadata } = await loadTournamentPredictions();
  const knockoutMatches = matches.filter((match) => match.round !== null);

  return (
    <PageContainer
      eyebrow="Knockout stage"
      title="Most likely bracket"
      description="Projected knockout matchups derived from synchronized tournament predictions."
    >
      <p className="rounded-xl border border-dashed bg-card/60 px-4 py-3 text-sm text-muted-foreground">
        Loaded from the latest synchronized tournament predictions
        {typeof metadata.simulations === "number" ? ` · ${metadata.simulations.toLocaleString("en")} simulations` : ""}.
      </p>
      <BracketSummary matches={knockoutMatches} />
    </PageContainer>
  );
}
