import type { Locale } from "@/lib/i18n/config";

export function teamNameToSlug(teamName: string): string {
  return teamName
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function teamHref(lang: Locale, teamName: string): string {
  return `/${lang}/teams/${teamNameToSlug(teamName)}`;
}
