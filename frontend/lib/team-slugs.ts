export function teamNameToSlug(teamName: string): string {
  return teamName
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function teamHref(teamName: string): `/teams/${string}` {
  return `/teams/${teamNameToSlug(teamName)}`;
}
