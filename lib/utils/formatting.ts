export type NumberFormatOptions = Intl.NumberFormatOptions & { locale?: string };

export function formatNumber(value: number, { locale, ...options }: NumberFormatOptions = {}): string {
  return new Intl.NumberFormat(locale, options).format(value);
}

export function formatCurrency(value: number, currency: string, options: NumberFormatOptions = {}): string {
  return formatNumber(value, { ...options, style: "currency", currency });
}

export function formatPercent(value: number, options: NumberFormatOptions = {}): string {
  return formatNumber(value, { ...options, style: "percent" });
}

export function formatDate(value: Date | string, options: Intl.DateTimeFormatOptions = { dateStyle: "medium" }, locale?: string): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return new Intl.DateTimeFormat(locale, options).format(date);
}

export function formatBytes(value: number, locale?: string): string {
  if (!Number.isFinite(value) || value < 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"] as const;
  const index = Math.min(Math.floor(Math.log(Math.max(value, 1)) / Math.log(1024)), units.length - 1);
  return `${formatNumber(value / 1024 ** index, { ...(locale ? { locale } : {}), maximumFractionDigits: index === 0 ? 0 : 1 })} ${units[index]}`;
}
