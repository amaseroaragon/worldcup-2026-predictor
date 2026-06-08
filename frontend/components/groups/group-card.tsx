import { SectionCard } from "@/components/layout/section-card";
import { formatOptionalNumber, formatOptionalPercent } from "@/lib/formatters";
import type { GroupResultTeam } from "@/lib/types";

type GroupCardProps = {
  group: string;
  teams: GroupResultTeam[];
  projectedPoints: Record<string, number>;
};

const firstDefined = (...values: Array<number | null | undefined>) =>
  values.find((value) => value !== null && value !== undefined);

export function GroupCard({ group, teams, projectedPoints }: GroupCardProps) {
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
                <td className="py-3 pr-3 font-semibold">{team.team}</td>
                <td className="py-3 text-center font-semibold">{formatOptionalNumber(firstDefined(projectedPoints[team.team], team.points), 0)}</td>
                <td className="py-3 text-center">{formatOptionalNumber(firstDefined(team.expected_goals_for, team.goals_for))}</td>
                <td className="py-3 text-center">{formatOptionalNumber(firstDefined(team.expected_goals_against, team.goals_against))}</td>
                <td className="py-3 text-center">{formatOptionalNumber(firstDefined(team.expected_goal_difference, team.goal_difference))}</td>
                <td className="py-3 text-right font-semibold text-primary">{formatOptionalPercent(team.qualification_probability)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-4 text-[0.7rem] leading-5 text-muted-foreground">
        Points use the most likely predicted score for each group-stage match.
      </p>
    </SectionCard>
  );
}
