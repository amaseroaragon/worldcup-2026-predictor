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
export type TournamentRound = "Group stage" | "Round of 32" | "Round of 16" | "Quarter-final" | "Semi-final" | "Final";

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

export type PredictedMatch = Match & {
  matchNumber: number;
  homeWinProbability: number;
  drawProbability: number;
  awayWinProbability: number;
  predictedHomeScore: number;
  predictedAwayScore: number;
};

export type BracketRound = {
  name: Exclude<TournamentRound, "Group stage">;
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
  matches: PredictedMatch[];
  probabilities: TournamentProbabilities[];
};
