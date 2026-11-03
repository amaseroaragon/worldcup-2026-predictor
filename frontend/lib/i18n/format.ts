import type { Locale } from "./config";

/** Locale-aware number and date formatting, usable on server and client. */
export function formatter(lang: Locale) {
  const percent = (digits: number) => new Intl.NumberFormat(lang, { style: "percent", maximumFractionDigits: digits });
  const date = new Intl.DateTimeFormat(lang, { day: "numeric", month: "short", timeZone: "UTC" });

  return {
    /** "4.2%" below 10%, "17%" above (es: "4,2 %", "17 %"). */
    prob(value: number | null | undefined): string {
      if (value === null || value === undefined) return "—";
      if (value > 0 && value < 0.001) return `<${percent(1).format(0.001)}`;
      return percent(value < 0.1 ? 1 : 0).format(value);
    },
    num(value: number | null | undefined, digits = 1): string {
      if (value === null || value === undefined) return "—";
      return new Intl.NumberFormat(lang, { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);
    },
    int(value: number): string {
      return new Intl.NumberFormat(lang, { useGrouping: true }).format(Math.round(value));
    },
    date(iso: string): string {
      return date.format(new Date(iso));
    },
  };
}

export type Formatter = ReturnType<typeof formatter>;
