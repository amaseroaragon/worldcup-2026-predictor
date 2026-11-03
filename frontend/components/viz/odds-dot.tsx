import type { Locale } from "@/lib/i18n/config";
import { formatter } from "@/lib/i18n/format";
import { cn } from "@/lib/utils";

type OddsDotProps = {
  lang: Locale;
  value: number;
  /** Value at the right end of the axis. */
  max: number;
  highlight?: boolean;
  className?: string;
};

/** A dot on a hairline axis: compact, comparable across rows. */
export function OddsDot({ lang, value, max, highlight, className }: OddsDotProps) {
  const label = formatter(lang).prob(value);
  return (
    <span className={cn("flex items-center gap-3.5", className)}>
      <span className="relative h-px flex-1 bg-[#d6d6d6]" role="img" aria-label={label}>
        <span
          className={cn("absolute -top-[5px] size-2.5 rounded-full", highlight ? "bg-accent" : "bg-ink")}
          style={{ left: `calc(${Math.min(value / max, 1) * 100}% - 5px)` }}
        />
      </span>
      <span className="w-14 text-right font-mono text-[13px] tabular">{label}</span>
    </span>
  );
}
