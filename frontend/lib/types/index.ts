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

export type WorldCupProbability = {
  team: string;
  champion_probability: number;
  runner_up_probability: number;
  semifinal_probability: number;
};

export type RecentFormMetric = {
  form_5: number | null;
  form_10: number | null;
  form_20: number | null;
  matches_available: number;
};

export type SquadStrengthMetric = {
  squad_value: number;
  squad_strength_rating: number;
};

export type TeamMetric = {
  team: string;
  group: string;
  attack_rating: number | null;
  defense_rating: number | null;
  matches_used: number | null;
  recent_form: RecentFormMetric | null;
  squad_strength: SquadStrengthMetric | null;
};

export type GroupResultTeam = {
  position: number;
  team: string;
  expected_position?: number | null;
  expected_played?: number | null;
  expected_points?: number | null;
  points?: number | null;
  expected_goals_for?: number | null;
  goals_for?: number | null;
  expected_goals_against?: number | null;
  goals_against?: number | null;
  expected_goal_difference?: number | null;
  goal_difference?: number | null;
  qualification_probability?: number | null;
};

export type GroupResults = {
  metadata: {
    source: string;
    scope: string;
    simulations?: number;
  };
  groups: Record<string, GroupResultTeam[]>;
};

export type TournamentPredictionMatch = {
  match_id: string;
  stage: string;
  group: string | null;
  round: string | null;
  home_team: string;
  away_team: string;
  predicted_home_goals: number;
  predicted_away_goals: number;
  predicted_winner: string | null;
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  simulations_count: number | null;
  appearance_count: number | null;
  appearance_probability: number | null;
  average_home_goals: number | null;
  average_away_goals: number | null;
  most_common_score: string | null;
  source: string | null;
  user_home_goals: number | null;
  user_away_goals: number | null;
  real_home_goals: number | null;
  real_away_goals: number | null;
  prediction_correct: boolean | null;
};
