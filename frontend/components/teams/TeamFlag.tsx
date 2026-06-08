import { FALLBACK_TEAM_FLAG, TEAM_FLAGS } from "@/lib/data/teamFlags";
import { cn } from "@/lib/utils";

type TeamFlagProps = {
  team: string;
  size?: "sm" | "default" | "lg";
  className?: string;
};

export function TeamFlag({ team, size = "default", className }: TeamFlagProps) {
  return (
    <span
      aria-label={`${team} flag`}
      role="img"
      className={cn(
        "inline-flex shrink-0 items-center justify-center leading-none",
        size === "sm" && "text-lg",
        size === "default" && "text-2xl",
        size === "lg" && "text-4xl",
        className,
      )}
    >
      {TEAM_FLAGS[team] ?? FALLBACK_TEAM_FLAG}
    </span>
  );
}
