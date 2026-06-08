import { CompareTable } from "@/components/compare/compare-table";
import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { loadWorldCupProbabilities } from "@/lib/data/load-prediction-data";
import { formatPercent } from "@/lib/formatters";

export const metadata = { title: "Compare" };

export default async function ComparePage() {
  const probabilities = await loadWorldCupProbabilities();
  const rankedProbabilities = probabilities.toSorted(
    (a, b) => b.champion_probability - a.champion_probability,
  );
  const favourite = rankedProbabilities[0];

  return (
    <PageContainer
      eyebrow="Team analysis"
      title="Compare contenders"
      description="Compare aggregate tournament probabilities from the latest synchronized model output."
    >
      <section className="grid gap-4 sm:grid-cols-2">
        <SectionCard title="Teams analysed">
          <p className="text-3xl font-bold tracking-tight">{rankedProbabilities.length}</p>
          <p className="mt-1 text-sm text-muted-foreground">World Cup contenders in the model.</p>
        </SectionCard>
        <SectionCard title="Current favourite">
          {favourite ? (
            <>
              <TeamBadge team={favourite.team} size="lg" />
              <p className="mt-1 text-sm text-muted-foreground">
                {formatPercent(favourite.champion_probability, 1)} title probability
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">No probability data available.</p>
          )}
        </SectionCard>
      </section>

      <CompareTable probabilities={rankedProbabilities} />

      <SectionCard title="User predictions" description="Coming soon">
        <p className="text-sm leading-6 text-muted-foreground">
          Compare your bracket and tournament picks against the model.
        </p>
      </SectionCard>
    </PageContainer>
  );
}
