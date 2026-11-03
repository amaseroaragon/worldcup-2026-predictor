"use client";

import { useMemo, useState } from "react";

import { TeamLink } from "@/components/ui/primitives";
import { OutcomeBar, OutcomeKey, type OutcomeLabels } from "@/components/viz/outcome-bar";
import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { formatter } from "@/lib/i18n/format";
import { teamName } from "@/lib/i18n/teams";
import { cn } from "@/lib/utils";

import { ROUND_KEYS, type MatchRow } from "./types";

/** Plain-string slices of the dictionary (client components cannot receive functions). */
export type MatchesText = {
  ui: Dictionary["matchesUi"];
  outcome: OutcomeLabels;
  rounds: Dictionary["rounds"];
  /** "Group A" style labels, keyed by team. */
  groupLabelByTeam: Record<string, string>;
  /** Penalty note with a "{team}" placeholder. */
  penalties: string;
};

const COLUMNS = "md:grid-cols-[4rem_4.5rem_minmax(0,1fr)_4rem_minmax(0,16rem)_7rem_1.5rem]";

function HitMark({ row, text }: { row: MatchRow; text: MatchesText }) {
  if (row.hit === null) return null;
  const label = row.knockout
    ? row.hit
      ? text.ui.calledKnockout
      : text.ui.missedKnockout
    : row.hit
      ? text.ui.calledGroup
      : text.ui.missedGroup;
  return (
    <span
      role="img"
      aria-label={label}
      title={label}
      className={cn("inline-block size-2.5 rounded-full", row.hit ? "bg-accent" : "border border-hollow")}
    />
  );
}

export function MatchesExplorer({ rows, lang, text }: { rows: MatchRow[]; lang: Locale; text: MatchesText }) {
  const [round, setRound] = useState<(typeof ROUND_KEYS)[number]>("all");
  const [query, setQuery] = useState("");
  const filterLabels: Record<(typeof ROUND_KEYS)[number], string> = {
    all: text.ui.all,
    group: text.ui.groups,
    round_of_32: text.rounds.round_of_32,
    round_of_16: text.rounds.round_of_16,
    quarter_final: text.rounds.quarter_final,
    semi_final: text.rounds.semi_final,
    final: text.rounds.final,
  };

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matchesQuery = (team: string) =>
      team.toLowerCase().includes(q) || teamName(lang, team).toLowerCase().includes(q);
    return rows.filter(
      (row) =>
        (round === "all" ||
          (round === "final" ? row.roundKey === "final" || row.roundKey === "third_place_playoff" : row.roundKey === round)) &&
        (!q || matchesQuery(row.home) || matchesQuery(row.away)),
    );
  }, [rows, round, query, lang]);

  return (
    <div>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div role="group" aria-label={text.ui.round} className="scrollbar-none -mx-4 flex overflow-x-auto px-4 md:mx-0 md:px-0">
          <div className="flex overflow-hidden border bg-white text-sm">
            {ROUND_KEYS.map((key) => (
              <button
                key={key}
                type="button"
                aria-pressed={round === key}
                onClick={() => setRound(key)}
                className={cn(
                  "h-10 shrink-0 px-3.5",
                  round === key ? "bg-accent-soft font-medium text-accent-ink" : "text-muted hover:text-ink",
                )}
              >
                {filterLabels[key]}
              </button>
            ))}
          </div>
        </div>
        <label className="block md:w-64">
          <span className="sr-only">{text.ui.filterLabel}</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={text.ui.filterPlaceholder}
            className="h-10 w-full border bg-white px-3 text-sm placeholder:text-muted focus:border-ink focus:outline-none"
          />
        </label>
      </div>
      <OutcomeKey labels={text.outcome} className="mt-4" />

      <MatchList rows={visible} lang={lang} text={text} className="mt-6" />
      {visible.length === 0 && (
        <p className="mt-6 border border-dashed py-10 text-center text-sm text-muted">{text.ui.none}</p>
      )}
    </div>
  );
}

export function MatchList({
  rows,
  lang,
  text,
  className,
}: {
  rows: MatchRow[];
  lang: Locale;
  text: MatchesText;
  className?: string;
}) {
  if (rows.length === 0) return null;
  const fmt = formatter(lang);
  const roundLabel = (row: MatchRow) =>
    row.roundKey === "group"
      ? text.groupLabelByTeam[row.home]
      : text.rounds[row.roundKey as keyof MatchesText["rounds"]] ?? row.roundKey;

  return (
    <div className={cn("overflow-hidden border bg-white", className)}>
      <div className={`hidden gap-x-6 border-b bg-subtle px-5 py-2.5 text-xs text-muted md:grid ${COLUMNS}`}>
        <span>{text.ui.date}</span>
        <span>{text.ui.round}</span>
        <span>{text.ui.match}</span>
        <span className="text-right">{text.ui.score}</span>
        <span>{text.ui.model}</span>
        <span className="text-right">{text.ui.pick}</span>
        <span />
      </div>
      <ul>
        {rows.map((row) => {
          const ko = row.knockout;
          return (
            <li
              key={row.id}
              className={`grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 gap-y-2 border-b px-4 py-3.5 last:border-b-0 md:items-center md:gap-x-6 md:px-5 ${COLUMNS}`}
            >
              <span className="col-span-2 flex gap-3 text-xs text-muted md:contents">
                <span className="font-mono tabular">{fmt.date(row.date)}</span>
                <span>{roundLabel(row)}</span>
              </span>
              <span className="min-w-0 text-[15px]">
                <TeamLink lang={lang} team={row.home} className={row.winner === row.home ? "font-semibold" : ""} />
                <span className="mx-1.5 text-muted">{text.ui.versus}</span>
                <TeamLink lang={lang} team={row.away} className={row.winner === row.away ? "font-semibold" : ""} />
                {ko && (ko.pairingPredicted || ko.shootoutWinner) && (
                  <span className="mt-1.5 flex flex-wrap gap-1.5">
                    {ko.pairingPredicted && (
                      <span className="bg-accent-soft px-1.5 py-0.5 text-[11px] text-accent-ink">{text.ui.pairingPredicted}</span>
                    )}
                    {ko.shootoutWinner && (
                      <span className="bg-subtle px-1.5 py-0.5 text-[11px] text-ink-2 ring-1 ring-line">
                        {text.penalties.replace("{team}", teamName(lang, ko.shootoutWinner))}
                      </span>
                    )}
                  </span>
                )}
              </span>
              <span className="text-right font-mono text-[15px] font-medium tabular">
                {row.homeScore}–{row.awayScore}
              </span>
              {row.probabilities && (
                <span className="col-span-2 md:col-span-1">
                  <OutcomeBar lang={lang} labels={text.outcome} {...row.probabilities} actual={row.actual} />
                  {ko && (
                    <span className="mt-1 flex justify-between text-[11px] text-ink-2">
                      <span>
                        {fmt.prob(ko.homeAdvance)} {text.ui.toAdvance}
                      </span>
                      <span>{fmt.prob(ko.awayAdvance)}</span>
                    </span>
                  )}
                </span>
              )}
              {ko ? (
                <span className="hidden truncate text-right text-[13px] text-ink-2 md:block">{teamName(lang, ko.favourite)}</span>
              ) : (
                <span className="hidden text-right font-mono text-[13px] text-muted tabular md:block">{row.predictedScore}</span>
              )}
              <span className="hidden justify-self-end md:block">
                <HitMark row={row} text={text} />
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
