import Link from "next/link";
import { ArrowRight, BarChart3, GitCompareArrows, Trophy } from "lucide-react";

import { ProbabilityChart } from "@/components/charts/probability-chart";
import { ProbabilityBar } from "@/components/dashboard/probability-bar";
import { PageContainer } from "@/components/layout/page-container";
import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { buttonVariants } from "@/components/ui/button";
import { loadTournamentData } from "@/lib/data/load-tournament-data";
import { cn } from "@/lib/utils";

export default async function HomePage() {
  const { probabilities } = await loadTournamentData();
  const favorites = probabilities.slice(0, 5);

  return (
    <PageContainer
      eyebrow="Tournament overview"
      title="World Cup 2026 Predictor"
      description="Explore simulated outcomes, group projections and the road to the final."
    >
      <section className="grid gap-4 md:grid-cols-3">
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
        <SectionCard title="Top contenders" description="Mock Monte Carlo probabilities">
          <div className="space-y-5">
            {favorites.map((item) => (
              <div key={item.team.id}>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <TeamBadge team={item.team} href={`/teams/${item.team.slug}`} />
                  <span className="text-sm font-semibold">
                    {Math.round(item.winTournament * 100)}%
                  </span>
                </div>
                <ProbabilityBar value={item.winTournament} />
              </div>
            ))}
          </div>
        </SectionCard>
        <SectionCard title="Title probability" description="Initial Recharts integration">
          <ProbabilityChart data={favorites} />
        </SectionCard>
      </section>
    </PageContainer>
  );
}
