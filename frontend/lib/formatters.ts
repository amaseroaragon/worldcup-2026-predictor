export function formatPercent(value: number, maximumFractionDigits = 0): string {
  return new Intl.NumberFormat("en", {
    style: "percent",
    maximumFractionDigits,
  }).format(value);
}

export function formatOptionalNumber(
  value: number | null | undefined,
  maximumFractionDigits = 1,
): string {
  if (value === null || value === undefined) return "—";

  return new Intl.NumberFormat("en", { maximumFractionDigits }).format(value);
}

export function formatOptionalPercent(
  value: number | null | undefined,
  maximumFractionDigits = 0,
): string {
  return value === null || value === undefined
    ? "—"
    : formatPercent(value, maximumFractionDigits);
}

/** Percent with one decimal below 10% and none above, e.g. "4.2%", "17%". */
export function formatProb(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  if (value > 0 && value < 0.001) return "<0.1%";
  return formatPercent(value, value < 0.1 ? 1 : 0);
}

/** "1 in 6" style odds for a probability. */
export function formatOneIn(value: number): string {
  if (value <= 0) return "—";
  return `1 in ${Math.round(1 / value)}`;
}
