import type { ReactNode } from "react";

import { Card, CardHeader, Mono, TeamLink } from "@/components/ui/primitives";
import { OddsDot } from "@/components/viz/odds-dot";
import { StageTrack } from "@/components/viz/stage-track";
import type { Dictionary } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n/config";
import { formatter } from "@/lib/i18n/format";
import type { ActualStage } from "@/lib/types";

export type ForecastRow = {
  team: string;
  group: string;
  elo: number;
  eloRank: number;
  champion: number;
  advance: number;
  semifinal: number;
  final: number;
  stage: ActualStage;
};

const COLUMNS = "md:grid-cols-[2.5rem_minmax(0,13rem)_4.5rem_minmax(0,1fr)_17rem]";
const COLUMNS_WIDE = "md:grid-cols-[2.5rem_minmax(0,12rem)_4.5rem_repeat(3,4.5rem)_minmax(0,1fr)_17rem]";

type ForecastTableProps = {
  lang: Locale;
  t: Dictionary;
  rows: ForecastRow[];
  axisMax: number;
  detailed?: boolean;
  title: string;
  footer?: ReactNode;
};

/** Title odds before kick-off next to how far each team really went. */
export function ForecastTable({ lang, t, rows, axisMax, detailed = false, title, footer }: ForecastTableProps) {
  const columns = detailed ? COLUMNS_WIDE : COLUMNS;
  const { prob } = formatter(lang);
  const labels = t.forecastTable;

  return (
    <Card>
      <CardHeader note={t.common.trackLegend}>{title}</CardHeader>
      <div className={`hidden gap-x-6 border-b px-5 py-2.5 text-xs text-muted md:grid ${columns}`}>
        <span>#</span>
        <span>{labels.team}</span>
        <span className="text-right">{labels.elo}</span>
        {detailed && (
          <>
            <span className="text-right">{labels.r32}</span>
            <span className="text-right">{labels.semi}</span>
            <span className="text-right">{labels.final}</span>
          </>
        )}
        <span>{labels.odds}</span>
        <span>{labels.howFar}</span>
      </div>
      <ol>
        {rows.map((row, index) => {
          const champion = row.stage === "champion";
          return (
            <li
              key={row.team}
              className={`grid grid-cols-[2rem_minmax(0,1fr)_auto] items-center gap-x-3 gap-y-2 border-b px-4 py-3 last:border-b-0 md:min-h-13 md:gap-x-6 md:px-5 md:py-0 ${champion ? "bg-accent/[0.04]" : ""} ${columns}`}
            >
              <Mono className="text-muted">{String(index + 1).padStart(2, "0")}</Mono>
              <span className="min-w-0 truncate text-[15px]">
                <TeamLink lang={lang} team={row.team} className={champion ? "font-bold text-accent" : "font-medium"} />
                <span className="ml-2 text-xs text-muted md:hidden">Elo {Math.round(row.elo)}</span>
              </span>
              <Mono className="hidden text-right text-ink-2 md:block">
                {Math.round(row.elo)}
                <span className="ml-1 text-[11px] text-muted">#{row.eloRank}</span>
              </Mono>
              {detailed && (
                <>
                  <Mono className="hidden text-right md:block">{prob(row.advance)}</Mono>
                  <Mono className="hidden text-right md:block">{prob(row.semifinal)}</Mono>
                  <Mono className="hidden text-right md:block">{prob(row.final)}</Mono>
                </>
              )}
              <OddsDot
                lang={lang}
                value={row.champion}
                max={axisMax}
                highlight={champion}
                className="col-span-2 col-start-2 md:col-span-1 md:col-start-auto"
              />
              <StageTrack stage={row.stage} labels={t.stages} className="col-span-2 col-start-2 md:col-span-1 md:col-start-auto" />
            </li>
          );
        })}
      </ol>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t bg-subtle px-4 py-3 text-xs text-muted sm:px-5">
        <span>{labels.axis(Math.round(axisMax * 100))}</span>
        {footer}
      </div>
    </Card>
  );
}
