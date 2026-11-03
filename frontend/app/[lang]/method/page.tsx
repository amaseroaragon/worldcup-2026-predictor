import { Card, CardHeader, Figures, Mono, Page, Section } from "@/components/ui/primitives";
import { loadForecastVsActual } from "@/lib/data/load-prediction-data";
import { REPORT_URLS } from "@/lib/i18n/config";
import { pageContext, pageTitle } from "@/lib/i18n/page";
import { BACKTEST_TOURNAMENTS, backtestSummary } from "@/lib/model-validation";
import { cn } from "@/lib/utils";

export async function generateMetadata({ params }: PageProps<"/[lang]/method">) {
  return pageTitle(params, "method");
}

/** Mean binary Brier score for "team X is champion" if every team had probability 1/N. */
function uniformBrier(teams: number) {
  return (teams - 1) / (teams * teams);
}

export default async function MethodPage({ params }: PageProps<"/[lang]/method">) {
  const { lang, t, fmt, team } = await pageContext(params);
  const { summary, teams } = await loadForecastVsActual();
  const brier2026 =
    teams.reduce((total, row) => total + (row.champion_probability - Number(row.team === summary.champion)) ** 2, 0) /
    teams.length;
  const backtest = backtestSummary();
  const m = t.method;

  const rows = [
    ...BACKTEST_TOURNAMENTS.map((row) => ({
      id: row.id,
      winner: row.realChampion,
      rank: row.realChampionRankBySeed.toSorted((a, b) => a - b)[2],
      odds: row.realChampionProbability,
      favourite: `${team(row.modelFavorite)} ${fmt.prob(row.favoriteProbability)}`,
      brier: fmt.num(row.brierChampion, 4),
      baseline: fmt.num(uniformBrier(row.teams), 4),
      live: false,
    })),
    {
      id: "world_cup_2026",
      winner: summary.champion,
      rank: summary.champion_rank,
      odds: summary.champion_probability,
      favourite: m.reachedFinal(team(summary.model_favourite)),
      brier: fmt.num(brier2026, 4),
      baseline: fmt.num(uniformBrier(teams.length), 4),
      live: true,
    },
  ];

  return (
    <Page>
      <Figures
        items={[
          { label: m.history, value: fmt.int(49405), note: m.historyNote },
          { label: m.simulations, value: fmt.int(10000), note: m.simulationsNote },
          { label: m.backtest, value: `${backtest.top5}/${backtest.runs}`, note: m.backtestNote },
          { label: m.year, value: `#${summary.champion_rank}`, note: m.yearNote(team(summary.champion)) },
        ]}
      />

      <Section className="grid gap-3 lg:grid-cols-12">
        <div className="flex flex-col justify-between gap-6 bg-accent p-5 text-white sm:p-6 lg:col-span-5">
          <p className="text-[13px] text-white/80">{m.formulaTitle}</p>
          <pre className="overflow-x-auto font-mono text-[13px] leading-loose sm:text-sm">
            <code>
              λ<sub>A</sub> = 1.35 · e<sup>0.0015·(Elo<sub>A</sub>−Elo<sub>B</sub>)</sup>
              {"\n"}    · {m.formulaAttack}<sub>A</sub> · {m.formulaDefence}<sub>B</sub>
              {"\n"}    · {m.formulaForm}<sub>A</sub> · {m.formulaSquad}<sub>A</sub>
              {"\n"}
              <span className="text-white/75">{m.formulaRange}</span>
            </code>
          </pre>
          <p className="text-xs text-white/80">{m.formulaNote}</p>
        </div>
        <dl className="grid gap-3 sm:grid-cols-2 lg:col-span-7">
          {m.terms.map(([term, text]) => (
            <div key={term} className="border bg-white p-5 text-sm">
              <dt className="font-semibold">{term}</dt>
              <dd className="mt-1.5 text-ink-2">{text}</dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section>
        <Card>
          <CardHeader note={m.tableNote}>{m.table}</CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[42rem] text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted">
                  <th className="py-2.5 pl-5 font-normal">{m.tournament}</th>
                  <th className="py-2.5 font-normal">{m.winner}</th>
                  <th className="py-2.5 text-right font-normal">{m.rank}</th>
                  <th className="py-2.5 text-right font-normal">{m.winnerOdds}</th>
                  <th className="py-2.5 pl-6 font-normal">{m.favourite}</th>
                  <th className="py-2.5 text-right font-normal">{m.brier}</th>
                  <th className="py-2.5 pr-5 text-right font-normal">{m.equal}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.id} className={cn("h-12 border-b last:border-b-0", row.live && "bg-accent/[0.05]")}>
                    <td className="pl-5">
                      {m.tournaments[row.id]}
                      {row.live && (
                        <span className="ml-2 bg-accent-soft px-2 py-0.5 text-[11px] font-medium text-accent-ink">
                          {m.thisForecast}
                        </span>
                      )}
                    </td>
                    <td className="font-medium">{team(row.winner)}</td>
                    <td className="text-right">
                      <Mono>#{row.rank}</Mono>
                    </td>
                    <td className="text-right">
                      <Mono>{fmt.prob(row.odds)}</Mono>
                    </td>
                    <td className="pl-6 text-ink-2">{row.favourite}</td>
                    <td className="text-right">
                      <Mono>{row.brier}</Mono>
                    </td>
                    <td className="pr-5 text-right">
                      <Mono className="text-muted">{row.baseline}</Mono>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </Section>

      <a
        href={REPORT_URLS[lang]}
        target="_blank"
        rel="noopener noreferrer"
        hrefLang={lang}
        className="mt-6 flex items-center justify-between border bg-white px-5 py-4 text-sm font-medium transition-colors hover:border-ink sm:mt-8"
      >
        {m.report}
        <span aria-hidden>→</span>
      </a>
    </Page>
  );
}
