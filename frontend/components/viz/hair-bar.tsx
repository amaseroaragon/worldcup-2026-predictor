import { cn } from "@/lib/utils";

/** 4px single-series bar on a light track. */
export function HairBar({ value, className, tone = "accent" }: { value: number; className?: string; tone?: "accent" | "ink" | "faint" }) {
  return (
    <span className={cn("block h-1 w-full bg-track", className)}>
      <span
        className={cn("block h-full", tone === "accent" ? "bg-accent" : tone === "ink" ? "bg-ink" : "bg-hollow")}
        style={{ width: `${Math.min(Math.max(value, 0), 1) * 100}%` }}
      />
    </span>
  );
}
