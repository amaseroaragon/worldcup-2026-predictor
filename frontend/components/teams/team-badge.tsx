import Link from "next/link";

import { TeamFlag } from "@/components/teams/TeamFlag";
import { teamHref } from "@/lib/team-slugs";
import { cn } from "@/lib/utils";

type TeamBadgeProps = {
  team: string;
  size?: "sm" | "default" | "lg";
  linked?: boolean;
  className?: string;
  nameClassName?: string;
};

export function TeamBadge({
  team,
  size = "default",
  linked = true,
  className,
  nameClassName,
}: TeamBadgeProps) {
  const content = (
    <>
      <TeamFlag team={team} size={size} />
      <span className={cn("font-semibold", size === "lg" && "text-xl", nameClassName)}>{team}</span>
    </>
  );
  const styles = cn(
    "inline-flex items-center gap-2 text-sm",
    linked && "transition hover:text-primary",
    className,
  );

  return linked ? (
    <Link href={teamHref(team)} className={styles}>{content}</Link>
  ) : (
    <span className={styles}>{content}</span>
  );
}
