export function formatPercent(value: number, maximumFractionDigits = 0): string {
  return new Intl.NumberFormat("en", {
    style: "percent",
    maximumFractionDigits,
  }).format(value);
}
