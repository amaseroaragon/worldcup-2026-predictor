export type Team = {
  id: string;
  name: string;
  slug: string;
  code: string;
  group: string;
  flagUrl?: string;
};

export type Group = {
  id: string;
  name: string;
  teams: Team[];
};

export type MatchStatus = "scheduled" | "completed";
export type TournamentRound = "Group" | "Round of 16" | "Quarter-final" | "Semi-final" | "Final";

export type Match = {
  id: string;
  round: TournamentRound;
  homeTeam: Team;
  awayTeam: Team;
  status: MatchStatus;
  kickoff?: string;
  homeScore?: number;
  awayScore?: number;
};

export type BracketRound = {
  name: Exclude<TournamentRound, "Group">;
  matches: Match[];
};

export type Bracket = {
  rounds: BracketRound[];
};

export type TournamentProbabilities = {
  team: Team;
  reachRoundOf16: number;
  reachQuarterFinal: number;
  reachSemiFinal: number;
  reachFinal: number;
  winTournament: number;
};

export type TournamentData = {
  groups: Group[];
  bracket: Bracket;
  probabilities: TournamentProbabilities[];
};
