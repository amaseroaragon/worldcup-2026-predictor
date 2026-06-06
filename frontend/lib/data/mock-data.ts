import type { Bracket, Group, PredictedMatch, Team, TournamentProbabilities } from "@/lib/types";

const team = (name: string, code: string, group: string): Team => ({
  id: code.toLowerCase(),
  name,
  slug: name.toLowerCase().replaceAll(" ", "-"),
  code,
  group,
});

export const mockTeams = [
  team("Argentina", "ARG", "A"), team("France", "FRA", "A"), team("Japan", "JPN", "A"), team("Canada", "CAN", "A"),
  team("Spain", "ESP", "B"), team("Brazil", "BRA", "B"), team("Morocco", "MAR", "B"), team("Mexico", "MEX", "B"),
  team("England", "ENG", "C"), team("Portugal", "POR", "C"), team("United States", "USA", "C"), team("South Korea", "KOR", "C"),
] satisfies Team[];

export const mockGroups: Group[] = ["A", "B", "C"].map((name) => ({
  id: name.toLowerCase(),
  name,
  teams: mockTeams.filter((item) => item.group === name),
}));

const [argentina, france, japan, canada, spain, brazil, morocco, mexico, england, portugal, usa, southKorea] = mockTeams;

export const mockProbabilities: TournamentProbabilities[] = [
  [spain, .94, .67, .43, .27, .16], [argentina, .93, .65, .41, .25, .15], [france, .92, .63, .40, .24, .14],
  [brazil, .90, .60, .37, .22, .12], [england, .89, .58, .35, .20, .11], [portugal, .86, .52, .30, .16, .08],
  [morocco, .72, .36, .17, .08, .03], [usa, .69, .31, .14, .06, .02], [japan, .65, .29, .12, .05, .02],
  [mexico, .61, .25, .10, .04, .01], [southKorea, .58, .22, .08, .03, .01], [canada, .52, .18, .06, .02, .01],
].map(([selectedTeam, reachRoundOf16, reachQuarterFinal, reachSemiFinal, reachFinal, winTournament]) => ({
  team: selectedTeam as Team,
  reachRoundOf16: reachRoundOf16 as number,
  reachQuarterFinal: reachQuarterFinal as number,
  reachSemiFinal: reachSemiFinal as number,
  reachFinal: reachFinal as number,
  winTournament: winTournament as number,
}));

export const mockBracket: Bracket = {
  rounds: [
    { name: "Round of 16", matches: [{ id: "r16-1", round: "Round of 16", homeTeam: argentina, awayTeam: usa, status: "scheduled" }, { id: "r16-2", round: "Round of 16", homeTeam: spain, awayTeam: japan, status: "scheduled" }] },
    { name: "Quarter-final", matches: [{ id: "qf-1", round: "Quarter-final", homeTeam: france, awayTeam: portugal, status: "scheduled" }] },
    { name: "Semi-final", matches: [{ id: "sf-1", round: "Semi-final", homeTeam: brazil, awayTeam: england, status: "scheduled" }] },
    { name: "Final", matches: [{ id: "f-1", round: "Final", homeTeam: argentina, awayTeam: spain, status: "scheduled" }] },
  ],
};

export const mockMatches: PredictedMatch[] = [
  { id: "m-1", matchNumber: 1, round: "Group stage", homeTeam: argentina, awayTeam: japan, status: "scheduled", homeWinProbability: .61, drawProbability: .23, awayWinProbability: .16, predictedHomeScore: 2, predictedAwayScore: 1 },
  { id: "m-2", matchNumber: 2, round: "Group stage", homeTeam: france, awayTeam: canada, status: "scheduled", homeWinProbability: .72, drawProbability: .18, awayWinProbability: .10, predictedHomeScore: 2, predictedAwayScore: 0 },
  { id: "m-3", matchNumber: 3, round: "Group stage", homeTeam: spain, awayTeam: morocco, status: "scheduled", homeWinProbability: .54, drawProbability: .27, awayWinProbability: .19, predictedHomeScore: 1, predictedAwayScore: 0 },
  { id: "m-4", matchNumber: 4, round: "Round of 32", homeTeam: brazil, awayTeam: mexico, status: "scheduled", homeWinProbability: .64, drawProbability: .21, awayWinProbability: .15, predictedHomeScore: 2, predictedAwayScore: 1 },
  { id: "m-5", matchNumber: 5, round: "Round of 16", homeTeam: england, awayTeam: portugal, status: "scheduled", homeWinProbability: .39, drawProbability: .29, awayWinProbability: .32, predictedHomeScore: 1, predictedAwayScore: 1 },
  { id: "m-6", matchNumber: 6, round: "Quarter-final", homeTeam: argentina, awayTeam: usa, status: "scheduled", homeWinProbability: .68, drawProbability: .20, awayWinProbability: .12, predictedHomeScore: 2, predictedAwayScore: 0 },
  { id: "m-7", matchNumber: 7, round: "Semi-final", homeTeam: brazil, awayTeam: france, status: "scheduled", homeWinProbability: .34, drawProbability: .30, awayWinProbability: .36, predictedHomeScore: 1, predictedAwayScore: 1 },
  { id: "m-8", matchNumber: 8, round: "Final", homeTeam: argentina, awayTeam: spain, status: "scheduled", homeWinProbability: .35, drawProbability: .29, awayWinProbability: .36, predictedHomeScore: 1, predictedAwayScore: 1 },
];
