"use client";

import Link from "next/link";
import { useState } from "react";

import type { Locale } from "@/lib/i18n/config";
import type { Dictionary } from "@/lib/i18n/dictionaries/en";
import { teamName } from "@/lib/i18n/teams";
import { teamHref } from "@/lib/team-slugs";
import { cn } from "@/lib/utils";

import type { BracketCard, BracketViewData } from "./types";

type Views = { actual: BracketViewData; model: BracketViewData };

function Card({ card, final, lang, finalLabel }: { card: BracketCard; final?: boolean; lang: Locale; finalLabel: string }) {
  return (
    <div className={cn(" border bg-white px-3 py-2", final && "border-accent ring-1 ring-accent")}>
      {card.teams.map((team) => (
        <div key={team.team} className="flex h-6 items-center gap-2 text-[13px]">
          <span
            aria-hidden
            className={cn("size-1.5 shrink-0 rounded-full", team.mark ? "bg-accent" : "bg-transparent")}
          />
          <Link
            href={teamHref(lang, team.team)}
            className={cn("min-w-0 flex-1 truncate hover:text-accent", team.winner ? "font-semibold" : "text-muted")}
          >
            {teamName(lang, team.team)}
          </Link>
          <span className={cn("font-mono text-xs tabular", team.winner ? "text-ink" : "text-muted")}>{team.score}</span>
        </div>
      ))}
      {card.note && <p className="pl-3.5 text-[11px] text-muted">{card.note}</p>}
      {final && <p className="mt-1 border-t pt-1.5 pl-3.5 text-[11px] font-medium text-accent">{finalLabel}</p>}
    </div>
  );
}

export function BracketView({ views, lang, ui }: { views: Views; lang: Locale; ui: Dictionary["bracketUi"] }) {
  const [view, setView] = useState<keyof Views>("actual");
  const [round, setRound] = useState(0);
  const data = views[view];

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div role="group" aria-label={ui.viewLabel} className="inline-flex overflow-hidden border bg-white text-sm">
          {(["actual", "model"] as const).map((key) => (
            <button
              key={key}
              type="button"
              aria-pressed={view === key}
              onClick={() => setView(key)}
              className={cn("h-10 px-4", view === key ? "bg-accent-soft font-medium text-accent-ink" : "text-muted hover:text-ink")}
            >
              {key === "actual" ? ui.actual : ui.model}
            </button>
          ))}
        </div>
        <p className="flex items-center gap-1.5 text-xs text-muted">
          <span className="size-1.5 rounded-full bg-accent" /> {data.markLabel}
        </p>
      </div>

      <div className="mt-8 lg:hidden">
        <div role="tablist" aria-label={ui.roundLabel} className="grid grid-cols-5 overflow-hidden border bg-white text-sm">
          {data.rounds.map((item, index) => (
            <button
              key={item.label}
              type="button"
              role="tab"
              aria-selected={round === index}
              onClick={() => setRound(index)}
              className={cn("h-11", round === index ? "bg-accent-soft font-semibold text-accent-ink" : "text-muted hover:text-ink")}
            >
              {ui.roundsShort[index]}
            </button>
          ))}
        </div>
        <div role="tabpanel" className="mt-3 grid gap-2 sm:grid-cols-2">
          {data.rounds[round].cards.map((card) => (
            <Card key={card.id} card={card} final={round === data.rounds.length - 1} lang={lang} finalLabel={ui.final} />
          ))}
        </div>
      </div>

      <div className="mt-8 hidden lg:block">
        <div className="grid grid-cols-5 gap-6 pb-2 text-xs font-medium text-muted">
          {data.rounds.map((item, index) => (
            <span key={item.label}>{ui.rounds[index]}</span>
          ))}
        </div>
        <div className="grid grid-cols-5 gap-6" style={{ height: `${data.leafCount * 5.75}rem` }}>
          {data.rounds.map((item, roundIndex) => (
            <div key={item.label} className="relative">
              {item.cards.map((card) => (
                <div
                  key={card.id}
                  className="absolute inset-x-0 -translate-y-1/2"
                  style={{ top: `${((card.position + 0.5) / data.leafCount) * 100}%` }}
                >
                  <Card card={card} final={roundIndex === data.rounds.length - 1} lang={lang} finalLabel={ui.final} />
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
