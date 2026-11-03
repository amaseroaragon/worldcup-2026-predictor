export type MatchRow = {
  id: number;
  date: string;
  roundKey: string;
  home: string;
  away: string;
  homeScore: number;
  awayScore: number;
  winner: string | null;
  /** 90-minute win / draw / loss from the model, before kick-off. */
  probabilities?: { home: number; draw: number; away: number };
  /** What happened after 90 minutes (group matches only: knockout scores include extra time). */
  actual?: "home" | "draw" | "away";
  predictedScore?: string;
  /** Knockouts only. */
  knockout?: {
    homeAdvance: number;
    awayAdvance: number;
    favourite: string;
    pairingPredicted: boolean;
    shootoutWinner: string | null;
  };
  hit: boolean | null;
};

export const ROUND_KEYS = ["all", "group", "round_of_32", "round_of_16", "quarter_final", "semi_final", "final"] as const;
