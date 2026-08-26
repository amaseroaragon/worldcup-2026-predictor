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
      title="Deterministic bracket"
      description="A single projected bracket using the model's deterministic match outcomes."
    >
      <p className="rounded-xl border border-dashed bg-card/60 px-4 py-3 text-sm text-muted-foreground">
        Based on the model&apos;s deterministic match outcomes
        {typeof metadata.simulations === "number" ? ` · ${metadata.simulations.toLocaleString("en")} simulations` : ""}.
      </p>
      <p className="text-xs text-muted-foreground">
        On smaller screens, scroll horizontally to follow the projected path to the final.
      </p>
      <BracketSummary matches={knockoutMatches} />
    </PageContainer>
  );
}
