import Link from "next/link";
import { notFound } from "next/navigation";

import { MatchList } from "@/components/matches/matches-explorer";
import { Card, CardHeader, Figures, Label, Mono, Page, Section } from "@/components/ui/primitives";
import { HairBar } from "@/components/viz/hair-bar";
import { OutcomeKey } from "@/components/viz/outcome-bar";
import { StageTrack } from "@/components/viz/stage-track";
import { loadEloRatings, loadForecastVsActual, loadTeamProfiles } from "@/lib/data/load-prediction-data";
import { buildMatchRows } from "@/lib/data/match-rows";
import { getDictionary } from "@/lib/i18n";
import { hasLocale } from "@/lib/i18n/config";
import { buildMatchesText } from "@/lib/i18n/matches-text";
import { pageContext } from "@/lib/i18n/page";
import { teamName } from "@/lib/i18n/teams";
import { reachedAtLeast } from "@/lib/stages";
import { teamNameToSlug } from "@/lib/team-slugs";
import type { ActualStage, TeamProfile } from "@/lib/types";
import { cn } from "@/lib/utils";

export async function generateStaticParams() {
  const profiles = await loadTeamProfiles();
  return profiles.map(({ metric }) => ({ team: teamNameToSlug(metric.team) }));
}

export async function generateMetadata({ params }: PageProps<"/[lang]/teams/[team]">) {
  const { lang, team: slug } = await params;
  const profile = (await loadTeamProfiles()).find(({ metric }) => teamNameToSlug(metric.team) === slug);
  if (!profile || !hasLocale(lang)) return { title: getDictionary("en").meta.pages.teams };
  return { title: teamName(lang, profile.metric.team) };
}

type MetricKey = "attack" | "defense" | "form" | "squad";

const METRICS: Array<{ key: MetricKey; higherIsBetter: boolean }> = [
  { key: "attack", higherIsBetter: true },
  { key: "defense", higherIsBetter: false },
  { key: "form", higherIsBetter: true },
  { key: "squad", higherIsBetter: true },
];

function metricValue(profile: TeamProfile, key: MetricKey): number | null {
  const { metric } = profile;
  if (key === "attack") return metric.attack_rating;
  if (key === "defense") return metric.defense_rating;
  if (key === "form") return metric.recent_form?.form_10 ?? null;
  return metric.squad_strength?.squad_strength_rating ?? null;
}

function metricRank(profiles: TeamProfile[], profile: TeamProfile, item: (typeof METRICS)[number]) {
  const value = metricValue(profile, item.key);
  if (value === null) return null;
  const values = profiles.map((p) => metricValue(p, item.key)).filter((v): v is number => v !== null);
  return 1 + values.filter((v) => (item.higherIsBetter ? v > value : v < value)).length;
}

export default async function TeamPage({ params }: PageProps<"/[lang]/teams/[team]">) {
  const { lang, t, fmt } = await pageContext(params);
  const { team: slug } = await params;
  const [profiles, report, elo] = await Promise.all([loadTeamProfiles(), loadForecastVsActual(), loadEloRatings()]);
  const profile = profiles.find(({ metric }) => teamNameToSlug(metric.team) === slug);
  if (!profile) notFound();

  const name = profile.metric.team;
  const outcome = report.teams.find((row) => row.team === name);
  const rating = elo.teams.find((row) => row.team === name);
  if (!outcome || !rating) notFound();

  const s = t.team;
  const stageTargets: ActualStage[] = ["round_of_32", "semi_final", "final", "champion"];
  const stageProbabilities = [
    outcome.qualification_probability,
    outcome.semifinal_probability,
    outcome.final_probability,
    outcome.champion_probability,
  ];
  const matches = buildMatchRows(report).filter((row) => row.home === name || row.away === name);

  return (
    <Page>
      <Link href={`/${lang}/teams`} className="text-xs text-muted hover:text-ink">
        {s.back}
      </Link>
      <Figures
        className="mt-6"
        items={[
          { label: t.common.group(profile.metric.group), value: teamName(lang, name) },
          { label: s.elo, value: Math.round(rating.elo), note: s.eloNote(rating.field_rank, rating.world_rank) },
          { label: s.odds, value: fmt.prob(outcome.champion_probability), note: s.oddsNote(outcome.champion_rank) },
          { label: s.reached, value: t.stages[outcome.actual_stage] },
        ]}
      />

      <Section className="grid gap-3 lg:grid-cols-2">
        <Card>
          <CardHeader note={s.stagesNote}>{s.stages}</CardHeader>
          <ul>
            {s.stageRows.map((label, index) => {
              const reached = reachedAtLeast(outcome.actual_stage, stageTargets[index]);
              return (
                <li
                  key={label}
                  className="grid h-12 grid-cols-[minmax(0,1fr)_6rem_3.5rem_1.5rem] items-center gap-4 border-b px-4 text-sm sm:px-5"
                >
                  <span>{label}</span>
                  <HairBar value={stageProbabilities[index]} tone="ink" />
                  <Mono className="text-right">{fmt.prob(stageProbabilities[index])}</Mono>
                  <span
                    role="img"
                    aria-label={reached ? s.yes : s.no}
                    className={cn("size-2.5 justify-self-end rounded-full", reached ? "bg-accent" : "border border-hollow")}
                  />
                </li>
              );
            })}
          </ul>
          <div className="bg-subtle px-4 py-3.5 sm:px-5">
            <StageTrack stage={outcome.actual_stage} labels={t.stages} />
          </div>
        </Card>

        <Card>
          <CardHeader note={s.inputsNote}>{s.inputs}</CardHeader>
          <dl className="grid grid-cols-2 gap-px bg-line">
            {METRICS.map((item) => {
              const rank = metricRank(profiles, profile, item);
              const [label, note] = s.metrics[item.key];
              return (
                <div key={item.key} className="bg-white p-4 sm:p-5">
                  <dt className="text-[13px] text-muted">{label}</dt>
                  <dd className="mt-1 flex items-baseline gap-2">
                    <span className="font-mono text-xl tabular">{fmt.num(metricValue(profile, item.key), 2)}</span>
                    {rank && <Mono className="text-muted">#{rank}</Mono>}
                  </dd>
                  <dd className="mt-1 text-[11px] text-muted">{note}</dd>
                </div>
              );
            })}
          </dl>
        </Card>
      </Section>

      <Section>
        <Label note={<OutcomeKey labels={t.outcome} />}>{s.matches}</Label>
        <MatchList rows={matches} lang={lang} text={buildMatchesText(t, elo)} />
      </Section>
    </Page>
  );
}
