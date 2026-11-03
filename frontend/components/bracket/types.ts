export type CardTeam = { team: string; score: number; winner: boolean; mark: boolean };
export type BracketCard = { id: string; position: number; teams: [CardTeam, CardTeam]; note?: string };
export type BracketRound = { label: string; short: string; cards: BracketCard[] };
export type BracketViewData = { rounds: BracketRound[]; leafCount: number; markLabel: string };
