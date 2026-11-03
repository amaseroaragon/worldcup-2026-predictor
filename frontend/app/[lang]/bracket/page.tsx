import { BracketView } from "@/components/bracket/bracket-view";
import type { BracketRound } from "@/components/bracket/types";
import { Figures, Page, Section } from "@/components/ui/primitives";
import { positionBracketMatches, positionedRoundMatches } from "@/lib/bracket-layout";
import { loadForecastVsActual, loadRepresentativeTournament } from "@/lib/data/load-prediction-data";
import { pageContext, pageTitle } from "@/lib/i18n/page";
import { actualBracketTree, reachedAtLeast, roundToStage } from "@/lib/stages";
import type { ActualStage } from "@/lib/types";

export async function generateMetadata({ params }: PageProps<"/[lang]/bracket">) {
  return pageTitle(params, "bracket");
}

const ROUND_KEYS = ["round_of_32", "round_of_16", "quarter_final", "semi_final", "final"];

type Node = {
  match_id: string;
  round: string;
  source_match_ids: string[];
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  winner: string;
};

function toRounds<T extends Node>(
  nodes: T[],
  decorate: (node: T) => Pick<BracketRound["cards"][number], "teams" | "note">,
): BracketRound[] {
  const positions = positionBracketMatches(nodes);
  return ROUND_KEYS.map((key) => ({
    label: key,
    short: key,
    cards: positionedRoundMatches(
      nodes.filter((node) => node.round === key),
      positions,
    ).map(({ match, position }) => ({ id: match.match_id, position, ...decorate(match) })),
  }));
}

export default async function BracketPage({ params }: PageProps<"/[lang]/bracket">) {
  const { lang, t, fmt, team } = await pageContext(params);
  const [report, { representative_tournament: representative }] = await Promise.all([
    loadForecastVsActual(),
    loadRepresentativeTournament(),
  ]);
  const stageByTeam = new Map<string, ActualStage>(report.teams.map((row) => [row.team, row.actual_stage]));
  const actualTree = actualBracketTree(report.knockout_matches);
  const modelTree = representative.bracket.filter((match) => match.round !== "third_place_playoff") as Node[];
  const pairings = report.knockout_matches.filter((m) => m.pairing_predicted && m.stage !== "third_place_playoff").length;
  const finalMatch = report.knockout_matches.find((m) => m.stage === "final");
  const predictedFinal = representative.bracket.find((m) => m.round === "final");
  const b = t.bracket;

  const actual = {
    leafCount: 16,
    markLabel: t.bracketUi.actualMark,
    rounds: toRounds(actualTree, (node) => ({
      teams: [
        { team: node.home_team, score: node.home_score, winner: node.winner === node.home_team, mark: node.source.pairing_predicted },
        { team: node.away_team, score: node.away_score, winner: node.winner === node.away_team, mark: node.source.pairing_predicted },
      ],
      note: node.source.shootout_winner ? t.common.onPenalties(team(node.source.shootout_winner)) : undefined,
    })),
  };
  const model = {
    leafCount: 16,
    markLabel: t.bracketUi.modelMark,
    rounds: toRounds(modelTree, (node) => {
      const stage = roundToStage(node.round);
      const mark = (name: string) => reachedAtLeast(stageByTeam.get(name) ?? "group", stage);
      return {
        teams: [
          { team: node.home_team, score: node.home_score, winner: node.winner === node.home_team, mark: mark(node.home_team) },
          { team: node.away_team, score: node.away_score, winner: node.winner === node.away_team, mark: mark(node.away_team) },
        ],
      };
    }),
  };

  return (
    <Page>
      <Figures
        items={[
          {
            label: b.final,
            value: finalMatch ? `${team(finalMatch.home_team)} ${finalMatch.home_score}–${finalMatch.away_score}` : "—",
            note: finalMatch ? b.finalVs(team(finalMatch.away_team)) : undefined,
          },
          {
            label: b.modelFinal,
            value: predictedFinal ? `${team(predictedFinal.home_team)} ${predictedFinal.predicted_score.replace("-", "–")}` : "—",
            note: predictedFinal
              ? b.modelFinalNote(team(predictedFinal.away_team), fmt.prob(predictedFinal.appearance_probability))
              : undefined,
          },
          { label: b.pairings, value: `${pairings}/31`, note: b.pairingsNote },
          {
            label: b.semis,
            value: `${report.knockout_rounds.find((r) => r.stage === "semi_final")?.predicted_teams_correct ?? 0}/4`,
          },
        ]}
      />
      <Section>
        <BracketView views={{ actual, model }} lang={lang} ui={t.bracketUi} />
      </Section>
    </Page>
  );
}
