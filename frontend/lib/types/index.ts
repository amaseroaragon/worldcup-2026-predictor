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
  elo?: number | null;
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
  predicted_home_goals: number | null;
  predicted_away_goals: number | null;
  predicted_winner: string | null;
  advanced_by: "normal_time_win" | "higher_win_probability_after_draw" | null;
  home_win_probability: number | null;
  draw_probability: number | null;
  away_win_probability: number | null;
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

export type TournamentPredictions = {
  metadata: Record<string, unknown>;
  matches: TournamentPredictionMatch[];
};

export type RepresentativeStanding = {
  position: number;
  team: string;
  played: number;
  points: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  wins: number;
  draws: number;
  losses: number;
  qualification_probability: number | null;
};

export type RepresentativeBracketMatch = TournamentPredictionMatch & {
  home_score: number;
  away_score: number;
  predicted_score: string;
  winner: string;
  source: {
    home: string;
    away: string;
  };
  source_match_ids: string[];
};

export type RepresentativeTournament = {
  // Legacy JSON key; contents are the coherent deterministic displayed tournament.
  metadata: Record<string, unknown>;
  representative_tournament: {
    results: TournamentPredictionMatch[];
    groups: Record<string, RepresentativeStanding[]>;
    best_third_places: Array<RepresentativeStanding & {
      rank: number;
      group: string;
      qualified: boolean;
    }>;
    qualified: {
      group_winners: string[];
      runners_up: string[];
      best_third_places: string[];
      round_of_32: string[];
    };
    bracket: RepresentativeBracketMatch[];
    champion: string | null;
  };
};

export type TeamPredictionSummary = {
  group_position: number;
  points: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  qualified: boolean;
  stage_reached: string;
  displayed_matches: TournamentPredictionMatch[];
};

export type TeamProfile = {
  metric: TeamMetric;
  probability: WorldCupProbability | null;
  aggregateGroupResult: GroupResultTeam | null;
  predictionSummary: TeamPredictionSummary;
};

export type ActualStage =
  | "group"
  | "round_of_32"
  | "round_of_16"
  | "quarter_final"
  | "semi_final"
  | "final"
  | "champion";

export type EloRating = {
  team: string;
  group: string;
  elo: number;
  world_rank: number;
  field_rank: number;
  rating_date: string;
};

export type EloRatings = {
  metadata: Record<string, unknown>;
  teams: EloRating[];
};

export type ActualGroupMatch = {
  match_number: number;
  date: string;
  group: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  outcome: "home" | "draw" | "away";
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  predicted_outcome: "home" | "draw" | "away";
  predicted_home_goals: number;
  predicted_away_goals: number;
  outcome_hit: boolean;
  exact_score_hit: boolean;
  probability_of_actual_outcome: number;
  brier: number;
};

export type ActualKnockoutStage =
  | "round_of_32"
  | "round_of_16"
  | "quarter_final"
  | "semi_final"
  | "third_place_playoff"
  | "final";

export type ActualKnockoutMatch = {
  match_number: number;
  date: string;
  stage: ActualKnockoutStage;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  shootout_winner: string | null;
  winner: string;
  pairing_predicted: boolean;
  home_win_probability: number;
  draw_probability: number;
  away_win_probability: number;
  home_advance_probability: number;
  away_advance_probability: number;
  home_expected_goals: number;
  away_expected_goals: number;
  model_favourite: string;
  favourite_advanced: boolean;
  probability_of_actual_winner: number;
};

export type ForecastVsActual = {
  metadata: Record<string, unknown>;
  summary: {
    champion: string;
    runner_up: string;
    champion_probability: number;
    champion_rank: number;
    runner_up_rank: number;
    model_favourite: string;
    model_favourite_stage: ActualStage;
    predicted_final: [string, string];
    predicted_champion: string;
    final_pairing_predicted: boolean;
    qualified_correct: number;
    qualified_total: number;
    qualification_brier: number;
    qualification_baseline_brier: number;
    semifinal_brier: number;
    semifinal_baseline_brier: number;
  };
  group_stage: {
    summary: {
      matches: number;
      outcome_hits: number;
      exact_score_hits: number;
      mean_brier: number;
      baseline_mean_brier: number;
      mean_log_loss: number;
      baseline_log_loss: number;
      outcome_counts: Record<"home" | "draw" | "away", number>;
      predicted_draws: number;
    };
    matches: ActualGroupMatch[];
  };
  knockout_rounds: Array<{ stage: ActualKnockoutStage; teams: number; predicted_teams_correct: number }>;
  knockout_summary: {
    matches: number;
    favourite_advanced: number;
    advance_brier: number;
    baseline_advance_brier: number;
    advance_log_loss: number;
    baseline_advance_log_loss: number;
    method: string;
  };
  knockout_matches: ActualKnockoutMatch[];
  teams: Array<{
    team: string;
    actual_stage: ActualStage;
    qualification_probability: number;
    semifinal_probability: number;
    final_probability: number;
    champion_probability: number;
    champion_rank: number;
  }>;
};
