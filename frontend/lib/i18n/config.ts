export const LOCALES = ["en", "es"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "en";

export function hasLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

export const REPORT_URLS: Record<Locale, string> = {
  en: "/world-cup-2026-project-report-english.pdf",
  es: "/world-cup-2026-project-report.pdf",
};
