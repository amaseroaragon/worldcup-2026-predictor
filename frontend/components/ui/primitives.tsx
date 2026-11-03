import Link from "next/link";
import type { ReactNode } from "react";

import type { Locale } from "@/lib/i18n/config";
import { teamName } from "@/lib/i18n/teams";
import { teamHref } from "@/lib/team-slugs";
import { cn } from "@/lib/utils";

export function Page({ children }: { children: ReactNode }) {
  return <div className="mx-auto w-full max-w-[1240px] px-4 pb-8 pt-8 sm:px-10 sm:pt-12">{children}</div>;
}

/** White surface with a hairline border: the basic container on the grey canvas. */
export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn("overflow-hidden border bg-white", className)}>{children}</section>;
}

/** Tinted strip at the top of a card that names its content. */
export function CardHeader({ children, note, className }: { children: ReactNode; note?: ReactNode; className?: string }) {
  return (
    <div className={cn("flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1 border-b bg-subtle px-4 py-3 sm:px-5", className)}>
      <h2 className="text-sm font-semibold">{children}</h2>
      {note && <div className="text-xs text-muted">{note}</div>}
    </div>
  );
}

/** Small muted label that names a block of data outside a card. */
export function Label({ children, note, className }: { children: ReactNode; note?: ReactNode; className?: string }) {
  return (
    <div className={cn("mb-3 flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1", className)}>
      <h2 className="text-sm font-semibold">{children}</h2>
      {note && <div className="text-xs text-muted">{note}</div>}
    </div>
  );
}

export type Figure = { label: string; value: ReactNode; note?: ReactNode };

/** Key-figure tiles at the top of every page; the first one is the lead, set in ink. */
export function Figures({ items, className }: { items: Figure[]; className?: string }) {
  return (
    <dl className={cn("grid grid-cols-2 gap-2 sm:gap-3 lg:grid-cols-4", className)}>
      {items.map((item, index) => {
        const lead = index === 0;
        return (
          <div
            key={item.label}
            className={cn(
              "flex min-h-32 flex-col p-4 sm:min-h-36 sm:p-5",
              lead ? "bg-accent text-white" : "border bg-white",
            )}
          >
            <dt className={cn("text-[13px]", lead ? "text-white/80" : "text-muted")}>{item.label}</dt>
            <dd className="mt-auto pt-3 text-[24px] font-semibold leading-tight tracking-[-0.02em] sm:text-[32px]">{item.value}</dd>
            {item.note && <dd className={cn("mt-1 text-xs", lead ? "text-white/80" : "text-muted")}>{item.note}</dd>}
          </div>
        );
      })}
    </dl>
  );
}

export function Section({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn("mt-6 sm:mt-8", className)}>{children}</section>;
}

export function TeamLink({ lang, team, className }: { lang: Locale; team: string; className?: string }) {
  return (
    <Link href={teamHref(lang, team)} className={cn("hover:text-accent", className)}>
      {teamName(lang, team)}
    </Link>
  );
}

export function Mono({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cn("font-mono text-[13px] tabular", className)}>{children}</span>;
}
