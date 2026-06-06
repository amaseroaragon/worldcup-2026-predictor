import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import type { Group } from "@/lib/types";

export function GroupCard({ group }: { group: Group }) {
  return (
    <SectionCard title={`Group ${group.name}`}>
      <ol className="divide-y">
        {group.teams.map((team, index) => (
          <li key={team.id} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0">
            <span className="w-4 text-xs font-semibold text-muted-foreground">{index + 1}</span>
            <TeamBadge team={team} href={`/teams/${team.slug}`} />
          </li>
        ))}
      </ol>
    </SectionCard>
  );
}
