export type NumberFormatOptions = Intl.NumberFormatOptions & { locale?: string };
export type PercentInput = "ratio" | "percent";
export type PercentFormatOptions = NumberFormatOptions & { input?: PercentInput };
export type DateTimeFormatOptions = Intl.DateTimeFormatOptions & { locale?: string };
export type RelativeTimeFormatOptions = Intl.RelativeTimeFormatOptions & {
  locale?: string;
  now?: Date | number;
};

export function formatNumber(
  value: number,
  { locale, ...options }: NumberFormatOptions = {},
): string {
  return new Intl.NumberFormat(locale, options).format(value);
}

export function formatCurrency(
  value: number,
  currency: string,
  options: NumberFormatOptions = {},
): string {
  return formatNumber(value, { ...options, style: "currency", currency });
}

export function formatCompactNumber(value: number, options: NumberFormatOptions = {}): string {
  return formatNumber(value, { notation: "compact", maximumFractionDigits: 1, ...options });
}

export function formatPercent(
  value: number,
  { input = "ratio", ...options }: PercentFormatOptions = {},
): string {
  return formatNumber(input === "percent" ? value / 100 : value, {
    maximumFractionDigits: 1,
    ...options,
    style: "percent",
  });
}

export function formatDate(
  value: Date | string | number,
  { locale, ...options }: DateTimeFormatOptions = { dateStyle: "medium" },
): string {
  const date = typeof value === "string" ? new Date(value) : value;
  return new Intl.DateTimeFormat(
    locale,
    Object.keys(options).length === 0 ? { dateStyle: "medium" } : options,
  ).format(date);
}

export function formatTime(
  value: Date | string | number,
  options: DateTimeFormatOptions = {},
): string {
  return formatDate(value, { timeStyle: "short", ...options });
}

export function formatDateTime(
  value: Date | string | number,
  options: DateTimeFormatOptions = {},
): string {
  return formatDate(value, { dateStyle: "medium", timeStyle: "short", ...options });
}

const RELATIVE_UNITS: readonly [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 24 * 60 * 60 * 1000],
  ["month", 30 * 24 * 60 * 60 * 1000],
  ["week", 7 * 24 * 60 * 60 * 1000],
  ["day", 24 * 60 * 60 * 1000],
  ["hour", 60 * 60 * 1000],
  ["minute", 60 * 1000],
  ["second", 1000],
];

export function formatRelativeTime(
  value: Date | string | number,
  { locale, now = Date.now(), ...options }: RelativeTimeFormatOptions = {},
): string {
  const target =
    typeof value === "string"
      ? new Date(value).getTime()
      : value instanceof Date
        ? value.getTime()
        : value;
  const current = now instanceof Date ? now.getTime() : now;
  const difference = target - current;
  const [unit, milliseconds] = RELATIVE_UNITS.find(([, size]) => Math.abs(difference) >= size) ?? [
    "second",
    1000,
  ];
  return new Intl.RelativeTimeFormat(locale, { numeric: "auto", ...options }).format(
    Math.round(difference / milliseconds),
    unit,
  );
}

export function formatBytes(value: number, locale?: string): string {
  if (!Number.isFinite(value) || value < 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"] as const;
  const index = Math.min(
    Math.floor(Math.log(Math.max(value, 1)) / Math.log(1024)),
    units.length - 1,
  );
  return `${formatNumber(value / 1024 ** index, { ...(locale ? { locale } : {}), maximumFractionDigits: index === 0 ? 0 : 1 })} ${units[index]}`;
}
