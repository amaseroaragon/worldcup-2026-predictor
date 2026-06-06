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
