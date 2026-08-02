import type { MetricValueDto } from "@/lib/api/analytics-types";

export function metricValue(metrics: readonly MetricValueDto[], code: string): string | undefined {
  return metrics.find((metric) => metric.code === code)?.value;
}

export function metricNumber(metrics: readonly MetricValueDto[], code: string): number | undefined {
  const raw = metricValue(metrics, code);
  if (raw === undefined) return undefined;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : undefined;
}

export function sumMetricNumbers(
  metrics: readonly MetricValueDto[],
  codes: readonly string[],
): number {
  return codes.reduce((total, code) => total + (metricNumber(metrics, code) ?? 0), 0);
}
