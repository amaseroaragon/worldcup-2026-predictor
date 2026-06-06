"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { TournamentProbabilities } from "@/lib/types";

export function ProbabilityChart({ data }: { data: TournamentProbabilities[] }) {
  const chartData = data.map((item) => ({ name: item.team.code, probability: Math.round(item.winTournament * 100) }));

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 560, height: 288 }}>
        <BarChart data={chartData} margin={{ top: 8, right: 8, left: -25, bottom: 0 }}>
          <XAxis dataKey="name" tickLine={false} axisLine={false} />
          <YAxis unit="%" tickLine={false} axisLine={false} />
          <Tooltip cursor={{ fill: "var(--muted)" }} formatter={(value) => [`${value}%`, "Champion"]} />
          <Bar dataKey="probability" fill="var(--primary)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
