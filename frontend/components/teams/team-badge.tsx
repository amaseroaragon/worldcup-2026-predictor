import Link from "next/link";

import type { Team } from "@/lib/types";
import { cn } from "@/lib/utils";

type TeamBadgeProps = { team: Team; href?: string; size?: "default" | "lg" };

export function TeamBadge({ team, href, size = "default" }: TeamBadgeProps) {
  const content = (
    <>
      <span className={cn("grid size-8 place-items-center rounded-full bg-secondary text-xs font-bold", size === "lg" && "size-12 text-base")}>
        {team.code}
      </span>
      <span>
        <span className="block font-semibold">{team.name}</span>
        {size === "lg" && <span className="block text-sm font-normal text-muted-foreground">FIFA code: {team.code}</span>}
      </span>
    </>
  );

  const className = "inline-flex items-center gap-3 text-sm";
  return href ? <Link href={href} className={`${className} hover:text-primary`}>{content}</Link> : <div className={className}>{content}</div>;
}
