import Link from "next/link";
import { ArrowRight, BarChart3, CalendarDays, GitCompareArrows, Trophy } from "lucide-react";

import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { buttonVariants } from "@/components/ui/button";
import { loadWorldCupProbabilities } from "@/lib/data/load-prediction-data";
import { formatPercent } from "@/lib/formatters";
import { cn } from "@/lib/utils";

export default async function HomePage() {
  const probabilities = await loadWorldCupProbabilities();
  const favorites = probabilities
    .toSorted((a, b) => b.champion_probability - a.champion_probability)
    .slice(0, 5);

  return (
    <PageContainer
      eyebrow="Tournament overview"
      title="World Cup 2026 Predictor"
      description="Explore the dashboard structure that will present Python-generated tournament projections."
    >
      <p className="rounded-xl border border-dashed bg-card/60 px-4 py-3 text-sm text-muted-foreground">
        Overview probabilities loaded from the latest synchronized Python prediction exports.
      </p>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SectionCard title="Groups" icon={<BarChart3 className="size-5" />}>
          <p className="text-sm text-muted-foreground">
            Review projected group standings and qualification chances.
          </p>
          <Link href="/groups" className={cn(buttonVariants({ variant: "outline" }), "mt-5 w-full")}>
            Explore groups <ArrowRight />
          </Link>
        </SectionCard>
        <SectionCard title="Bracket" icon={<Trophy className="size-5" />}>
          <p className="text-sm text-muted-foreground">
            Follow the most likely route through every knockout round.
          </p>
          <Link href="/bracket" className={cn(buttonVariants({ variant: "outline" }), "mt-5 w-full")}>
            View bracket <ArrowRight />
          </Link>
        </SectionCard>
        <SectionCard title="Matches" icon={<CalendarDays className="size-5" />}>
          <p className="text-sm text-muted-foreground">
            Browse projected fixtures, probabilities and expected results.
          </p>
          <Link href="/matches" className={cn(buttonVariants({ variant: "outline" }), "mt-5 w-full")}>
            Browse matches <ArrowRight />
          </Link>
        </SectionCard>
        <SectionCard title="Compare" icon={<GitCompareArrows className="size-5" />}>
          <p className="text-sm text-muted-foreground">
            Compare tournament probabilities across leading teams.
          </p>
          <Link href="/compare" className={cn(buttonVariants({ variant: "outline" }), "mt-5 w-full")}>
            Compare teams <ArrowRight />
          </Link>
        </SectionCard>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
        <SectionCard title="Top contenders" description="Ranked by champion probability.">
          <div className="space-y-5">
            {favorites.map((item) => (
              <div key={item.team}>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <span className="font-semibold">{item.team}</span>
                  <span className="text-sm font-bold text-primary">
                    {formatPercent(item.champion_probability, 1)}
                  </span>
                </div>
                <ProbabilityBar value={item.champion_probability} />
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  <span>Runner-up {formatPercent(item.runner_up_probability, 1)}</span>
                  <span>Semi-final {formatPercent(item.semifinal_probability, 1)}</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
        <SectionCard title="Bracket preview">
          <div className="min-h-64" aria-label="Bracket preview placeholder" />
        </SectionCard>
      </section>
    </PageContainer>
  );
}
