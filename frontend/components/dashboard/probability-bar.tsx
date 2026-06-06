import { cn } from "@/lib/utils";

type ProbabilityBarProps = { value: number; className?: string };

export function ProbabilityBar({ value, className }: ProbabilityBarProps) {
  const normalizedValue = Math.min(Math.max(value, 0), 1);

  return (
    <div
      className={cn("h-2.5 overflow-hidden rounded-full bg-muted", className)}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(normalizedValue * 100)}
    >
      <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${normalizedValue * 100}%` }} />
    </div>
  );
}
