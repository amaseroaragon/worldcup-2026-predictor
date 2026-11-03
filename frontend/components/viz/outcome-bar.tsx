import type { Locale } from "@/lib/i18n/config";
import { formatter } from "@/lib/i18n/format";
import { cn } from "@/lib/utils";

type Outcome = "home" | "draw" | "away";
export type OutcomeLabels = { first: string; draw: string; second: string; happened: string };

type OutcomeBarProps = {
  lang: Locale;
  labels: OutcomeLabels;
  home: number;
  draw: number;
  away: number;
  actual?: Outcome;
  className?: string;
};

/** Win / draw / loss split. The segment that actually happened carries a tick below it. */
export function OutcomeBar({ lang, labels, home, draw, away, actual, className }: OutcomeBarProps) {
  const { prob } = formatter(lang);
  const segments: Array<{ key: Outcome; className: string; label: string; value: number }> = [
    { key: "home", className: "bg-ink", label: labels.first, value: home },
    { key: "draw", className: "bg-draw", label: labels.draw, value: draw },
    { key: "away", className: "bg-accent", label: labels.second, value: away },
  ];
  const total = home + draw + away || 1;

  return (
    <span className={cn("block", className)}>
      <span
        role="img"
        aria-label={segments.map((segment) => `${segment.label} ${prob(segment.value)}`).join(", ")}
        className="flex h-1.5 gap-0.5"
      >
        {segments.map((segment) => (
          <span
            key={segment.key}
            title={`${segment.label}: ${prob(segment.value)}`}
            className={cn("relative h-full min-w-0.5", segment.className)}
            style={{ width: `${(segment.value / total) * 100}%` }}
          >
            {actual === segment.key && <span className="absolute left-1/2 top-2.5 h-1.5 w-px -translate-x-1/2 bg-ink" />}
          </span>
        ))}
      </span>
      <span className="mt-3 flex justify-between font-mono text-[11px] text-muted tabular">
        {segments.map((segment) => (
          <span key={segment.key}>{prob(segment.value)}</span>
        ))}
      </span>
    </span>
  );
}

export function OutcomeKey({ labels, className }: { labels: OutcomeLabels; className?: string }) {
  return (
    <span className={cn("flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted", className)}>
      <span className="inline-flex items-center gap-1.5"><span className="h-1.5 w-3 bg-ink" />{labels.first}</span>
      <span className="inline-flex items-center gap-1.5"><span className="h-1.5 w-3 bg-draw" />{labels.draw}</span>
      <span className="inline-flex items-center gap-1.5"><span className="h-1.5 w-3 bg-accent" />{labels.second}</span>
      <span className="inline-flex items-center gap-1.5"><span className="h-2 w-px bg-ink" />{labels.happened}</span>
    </span>
  );
}
