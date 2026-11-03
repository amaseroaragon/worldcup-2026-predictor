import { ForecastTable } from "@/components/tables/forecast-table";
import { Figures, Page, Section } from "@/components/ui/primitives";
import { loadForecastRows } from "@/lib/data/forecast-rows";
import { loadForecastVsActual } from "@/lib/data/load-prediction-data";
import { pageContext, pageTitle } from "@/lib/i18n/page";

export async function generateMetadata({ params }: PageProps<"/[lang]/teams">) {
  return pageTitle(params, "teams");
}

export default async function TeamsPage({ params }: PageProps<"/[lang]/teams">) {
  const { lang, t, fmt, team } = await pageContext(params);
  const [rows, { summary }] = await Promise.all([loadForecastRows(), loadForecastVsActual()]);
  const ranked = rows.map((row, index) => ({ ...row, rank: index + 1 }));
  const semifinalists = ranked.filter((row) => ["semi_final", "final", "champion"].includes(row.stage));
  const deepestOutsider = ranked
    .filter((row) => ["quarter_final", "semi_final", "final", "champion"].includes(row.stage))
    .toSorted((a, b) => b.rank - a.rank)[0];
  const s = t.teams;

  return (
    <Page>
      <Figures
        items={[
          { label: s.count, value: rows.length, note: s.countNote },
          {
            label: s.semifinalists,
            value: semifinalists.map((row) => `#${row.rank}`).join(" "),
            note: semifinalists.map((row) => team(row.team)).join(", "),
          },
          {
            label: s.semiBrier,
            value: fmt.num(summary.semifinal_brier, 3),
            note: s.semiBrierNote(fmt.num(summary.semifinal_baseline_brier, 3)),
          },
          { label: s.outsider, value: team(deepestOutsider.team), note: s.outsiderNote(deepestOutsider.rank) },
        ]}
      />
      <Section>
        <ForecastTable lang={lang} t={t} rows={rows} axisMax={0.2} detailed title={s.table} />
      </Section>
    </Page>
  );
}
