import Link from "next/link";

import { ForecastTable } from "@/components/tables/forecast-table";
import { Card, CardHeader, Figures, Page, Section } from "@/components/ui/primitives";
import { HairBar } from "@/components/viz/hair-bar";
import { loadForecastRows } from "@/lib/data/forecast-rows";
import { loadForecastVsActual, loadRepresentativeTournament } from "@/lib/data/load-prediction-data";
import { pageContext } from "@/lib/i18n/page";

export default async function ResultPage({ params }: PageProps<"/[lang]">) {
  const { lang, t, fmt, team } = await pageContext(params);
  const [report, rows, representative] = await Promise.all([
    loadForecastVsActual(),
    loadForecastRows(),
    loadRepresentativeTournament(),
  ]);
  const { summary } = report;
  const group = report.group_stage.summary;
  const predictedFinal = representative.representative_tournament.bracket.find((m) => m.round === "final");
  const simulations = (report.metadata.forecast_simulations as number) ?? 10000;

  return (
    <Page>
      <Figures
        items={[
          {
            label: t.result.finalPairing,
            value: summary.final_pairing_predicted ? t.result.correct : t.result.missed,
            note: t.result.finalNote(summary.predicted_final.map(team).join(` ${t.matchesUi.versus} `), fmt.prob(predictedFinal?.appearance_probability)),
          },
          {
            label: t.result.champion,
            value: `#${summary.champion_rank} · ${fmt.prob(summary.champion_probability)}`,
            note: t.result.championNote(team(summary.champion), team(summary.predicted_champion)),
          },
          {
            label: t.result.groupMatches,
            value: `${group.outcome_hits}/${group.matches}`,
            note: t.result.groupNote(Math.round(group.matches / 3)),
          },
          { label: t.result.simulations, value: fmt.int(simulations), note: t.result.simulationsNote },
        ]}
      />

      <Section>
        <Card>
          <CardHeader note={t.result.roundsNote}>{t.result.rounds}</CardHeader>
          <ul className="grid grid-cols-2 gap-px bg-line sm:grid-cols-5">
            {report.knockout_rounds.map((round) => (
              <li key={round.stage} className="bg-white p-4 sm:p-5 [&:last-child]:col-span-2 sm:[&:last-child]:col-span-1">
                <span className="text-[13px] text-muted">{t.result.roundLabels[round.stage]}</span>
                <span className="mt-1 block font-mono text-2xl tabular">
                  {round.predicted_teams_correct}
                  <span className="text-base text-muted">/{round.teams}</span>
                </span>
                <HairBar value={round.predicted_teams_correct / round.teams} className="mt-3" />
              </li>
            ))}
          </ul>
        </Card>
      </Section>

      <Section>
        <ForecastTable
          lang={lang}
          t={t}
          rows={rows.slice(0, 16)}
          axisMax={0.2}
          title={t.result.table}
          footer={
            <Link href={`/${lang}/teams`} className="font-medium text-ink hover:text-accent">
              {t.result.allTeams}
            </Link>
          }
        />
      </Section>
    </Page>
  );
}
