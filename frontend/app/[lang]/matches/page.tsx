import { MatchesExplorer } from "@/components/matches/matches-explorer";
import { Figures, Page, Section } from "@/components/ui/primitives";
import { loadEloRatings, loadForecastVsActual } from "@/lib/data/load-prediction-data";
import { buildMatchRows } from "@/lib/data/match-rows";
import { buildMatchesText } from "@/lib/i18n/matches-text";
import { pageContext, pageTitle } from "@/lib/i18n/page";

export async function generateMetadata({ params }: PageProps<"/[lang]/matches">) {
  return pageTitle(params, "matches");
}

export default async function MatchesPage({ params }: PageProps<"/[lang]/matches">) {
  const { lang, t, fmt } = await pageContext(params);
  const [report, elo] = await Promise.all([loadForecastVsActual(), loadEloRatings()]);
  const group = report.group_stage.summary;
  const knockouts = report.knockout_summary;
  const m = t.matches;

  return (
    <Page>
      <Figures
        items={[
          { label: m.groupHits, value: `${group.outcome_hits}/${group.matches}`, note: m.groupHitsNote(Math.round(group.matches / 3)) },
          { label: m.knockoutHits, value: `${knockouts.favourite_advanced}/${knockouts.matches}`, note: m.knockoutHitsNote },
          { label: m.brier, value: fmt.num(group.mean_brier, 3), note: m.brierNote(fmt.num(group.baseline_mean_brier, 3)) },
          { label: m.draws, value: `${group.outcome_counts.draw}`, note: m.drawsNote(group.predicted_draws) },
        ]}
      />
      <Section>
        <MatchesExplorer rows={buildMatchRows(report)} lang={lang} text={buildMatchesText(t, elo)} />
      </Section>
    </Page>
  );
}
