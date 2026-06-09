import { BracketSummary } from "@/components/bracket/bracket-summary";
import { PageContainer } from "@/components/layout/page-container";
import { loadRepresentativeTournament } from "@/lib/data/load-prediction-data";

export const metadata = { title: "Bracket" };

export default async function BracketPage() {
  const { representative_tournament, metadata } = await loadRepresentativeTournament();
  const knockoutMatches = representative_tournament.bracket;

  return (
    <PageContainer
      eyebrow="Knockout stage"
      title="Representative bracket"
      description="One coherent predicted scenario, resolved from group qualifiers through the champion."
    >
      <p className="rounded-xl border border-dashed bg-card/60 px-4 py-3 text-sm text-muted-foreground">
        Loaded from the representative tournament scenario
        {typeof metadata.simulations === "number" ? ` · ${metadata.simulations.toLocaleString("en")} simulations` : ""}.
      </p>
      <p className="text-xs text-muted-foreground">
        On smaller screens, scroll horizontally to follow the projected path to the final.
      </p>
      <BracketSummary matches={knockoutMatches} />
    </PageContainer>
  );
}
