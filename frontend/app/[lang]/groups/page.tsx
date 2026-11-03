import { Card, CardHeader, Figures, Mono, Page, Section, TeamLink } from "@/components/ui/primitives";
import { HairBar } from "@/components/viz/hair-bar";
import { loadEloRatings, loadForecastVsActual, loadGroupResults } from "@/lib/data/load-prediction-data";
import { pageContext, pageTitle } from "@/lib/i18n/page";
import { actualGroupRows } from "@/lib/stages";
import { cn } from "@/lib/utils";

export async function generateMetadata({ params }: PageProps<"/[lang]/groups">) {
  return pageTitle(params, "groups");
}

export default async function GroupsPage({ params }: PageProps<"/[lang]/groups">) {
  const { lang, t, fmt, team } = await pageContext(params);
  const [{ groups }, report, elo] = await Promise.all([loadGroupResults(), loadForecastVsActual(), loadEloRatings()]);
  const actualRows = actualGroupRows(report.group_stage.matches);
  const advanced = new Set(report.teams.filter((row) => row.actual_stage !== "group").map((row) => row.team));
  const eloByTeam = new Map(elo.teams.map((row) => [row.team, row.elo]));
  const all = Object.values(groups).flat();
  const biggestMiss = all
    .filter((row) => !advanced.has(row.team))
    .toSorted((a, b) => (b.qualification_probability ?? 0) - (a.qualification_probability ?? 0))[0];
  const surprise = all
    .filter((row) => advanced.has(row.team))
    .toSorted((a, b) => (a.qualification_probability ?? 0) - (b.qualification_probability ?? 0))[0];
  const { summary } = report;
  const g = t.groups;

  return (
    <Page>
      <Figures
        items={[
          { label: g.qualifiers, value: `${summary.qualified_correct}/${summary.qualified_total}`, note: g.qualifiersNote },
          {
            label: g.brier,
            value: fmt.num(summary.qualification_brier, 3),
            note: g.brierNote(fmt.num(summary.qualification_baseline_brier, 3)),
          },
          { label: g.miss, value: team(biggestMiss.team), note: g.missNote(fmt.prob(biggestMiss.qualification_probability)) },
          { label: g.surprise, value: team(surprise.team), note: g.surpriseNote(fmt.prob(surprise.qualification_probability)) },
        ]}
      />

      <Section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {Object.entries(groups)
          .toSorted(([a], [b]) => a.localeCompare(b))
          .map(([group, teams]) => (
            <Card key={group}>
              <CardHeader note={g.advancedCount(teams.filter((row) => advanced.has(row.team)).length)}>
                {t.common.group(group)}
              </CardHeader>
              <table className="w-full text-sm">
                <caption className="sr-only">{t.common.group(group)}</caption>
                <thead>
                  <tr className="border-b text-left text-xs text-muted">
                    <th className="py-2 pl-4 font-normal sm:pl-5">{g.team}</th>
                    <th className="w-12 py-2 text-right font-normal">{g.elo}</th>
                    <th className="w-28 py-2 pl-4 font-normal">{g.toAdvance}</th>
                    <th className="w-[5.75rem] whitespace-nowrap py-2 pl-4 pr-4 text-right font-normal sm:pr-5">{g.real}</th>
                  </tr>
                </thead>
                <tbody>
                  {teams
                    .toSorted((a, b) => a.position - b.position)
                    .map((row) => {
                      const through = advanced.has(row.team);
                      const status = through ? t.common.advanced : t.common.eliminated;
                      return (
                        <tr key={row.team} className="h-11 border-b last:border-b-0">
                          <td className="max-w-0 truncate pl-4 pr-2 sm:pl-5">
                            <TeamLink lang={lang} team={row.team} className="font-medium" />
                          </td>
                          <td className="text-right">
                            <Mono className="text-ink-2">{Math.round(eloByTeam.get(row.team) ?? 0)}</Mono>
                          </td>
                          <td className="pl-4">
                            <span className="flex items-center gap-2">
                              <HairBar value={row.qualification_probability ?? 0} tone="ink" className="flex-1" />
                              <Mono className="w-11 text-right">{fmt.prob(row.qualification_probability)}</Mono>
                            </span>
                          </td>
                          <td className="whitespace-nowrap pl-4 pr-4 text-right sm:pr-5">
                            <span className="inline-flex items-center gap-2">
                              <Mono>{t.common.pts(actualRows.get(row.team)?.points ?? 0)}</Mono>
                              <span
                                role="img"
                                title={status}
                                aria-label={status}
                                className={cn("size-2.5 rounded-full", through ? "bg-accent" : "border border-hollow")}
                              />
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                </tbody>
              </table>
            </Card>
          ))}
      </Section>
      <p className="mt-4 flex flex-wrap items-center gap-4 text-xs text-muted">
        <span className="inline-flex items-center gap-1.5">
          <span className="size-2.5 rounded-full bg-accent" />
          {g.advanced}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="size-2.5 rounded-full border border-hollow" />
          {g.out}
        </span>
        <span>{g.footnote}</span>
      </p>
    </Page>
  );
}
