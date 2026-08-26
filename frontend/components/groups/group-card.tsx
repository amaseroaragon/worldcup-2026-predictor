import { SectionCard } from "@/components/layout/section-card";
import { TeamBadge } from "@/components/teams/team-badge";
import { formatOptionalNumber, formatOptionalPercent } from "@/lib/formatters";
import type { RepresentativeStanding } from "@/lib/types";

type GroupCardProps = {
  group: string;
  teams: RepresentativeStanding[];
};

export function GroupCard({ group, teams }: GroupCardProps) {
  return (
    <SectionCard title={`Group ${group}`}>
      <div className="overflow-x-auto">
        <table className="w-full min-w-md text-left text-xs">
          <thead className="border-b text-[0.65rem] uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="pb-3 pr-2 font-medium">Pos</th>
              <th className="pb-3 pr-3 font-medium">Team</th>
              <th className="pb-3 text-center font-medium">Pts</th>
              <th className="pb-3 text-center font-medium">GF</th>
              <th className="pb-3 text-center font-medium">GA</th>
              <th className="pb-3 text-center font-medium">GD</th>
              <th className="pb-3 text-right font-medium">Qual.</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {teams.map((team) => (
              <tr key={team.team}>
                <td className="py-3 pr-2 font-bold text-muted-foreground">{team.position}</td>
                <td className="py-3 pr-3"><TeamBadge team={team.team} size="sm" /></td>
                <td className="py-3 text-center font-semibold">{formatOptionalNumber(team.points, 0)}</td>
                <td className="py-3 text-center">{formatOptionalNumber(team.goals_for, 0)}</td>
                <td className="py-3 text-center">{formatOptionalNumber(team.goals_against, 0)}</td>
                <td className="py-3 text-center">{formatOptionalNumber(team.goal_difference, 0)}</td>
                <td className="py-3 text-right font-semibold text-primary">{formatOptionalPercent(team.qualification_probability)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-4 text-[0.7rem] leading-5 text-muted-foreground">
        Position, points and goal statistics reflect the representative results shown above.
      </p>
    </SectionCard>
  );
}
