"""Analytics aggregation helpers."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    DateRangeComparisonRecord,
    MetricDeltaRecord,
    MetricValueRecord,
    PeriodMetricsRecord,
)


class AggregationService:
    """Computes metric deltas for date range comparisons."""

    @staticmethod
    def compute_deltas(
        baseline: PeriodMetricsRecord,
        comparison: PeriodMetricsRecord,
    ) -> tuple[MetricDeltaRecord, ...]:
        """Compute per-metric deltas between two periods."""

        baseline_by_code = {metric.code: metric for metric in baseline.metrics}
        comparison_by_code = {metric.code: metric for metric in comparison.metrics}
        all_codes = sorted(set(baseline_by_code) | set(comparison_by_code))

        deltas: list[MetricDeltaRecord] = []
        for code in all_codes:
            baseline_metric = baseline_by_code.get(code)
            comparison_metric = comparison_by_code.get(code)
            baseline_value = baseline_metric.value if baseline_metric else "0"
            comparison_value = comparison_metric.value if comparison_metric else "0"
            reference_metric = baseline_metric or comparison_metric
            unit = reference_metric.unit if reference_metric is not None else "count"
            is_estimated = bool(
                (baseline_metric and baseline_metric.is_estimated)
                or (comparison_metric and comparison_metric.is_estimated)
            )
            deltas.append(
                MetricDeltaRecord(
                    code=code,
                    unit=unit,
                    baseline_value=baseline_value,
                    comparison_value=comparison_value,
                    change_percent=AggregationService._change_percent(
                        baseline_value,
                        comparison_value,
                    ),
                    is_estimated=is_estimated,
                )
            )
        return tuple(deltas)

    @staticmethod
    def enrich_comparison(record: DateRangeComparisonRecord) -> DateRangeComparisonRecord:
        """Recompute deltas on a comparison record from its period metrics."""

        deltas = AggregationService.compute_deltas(record.baseline, record.comparison)
        return DateRangeComparisonRecord(
            baseline=record.baseline,
            comparison=record.comparison,
            deltas=deltas,
            time_zone=record.time_zone,
            fresh_through=record.fresh_through,
        )

    @staticmethod
    def _change_percent(baseline_value: str, comparison_value: str) -> str | None:
        try:
            baseline = Decimal(baseline_value)
            comparison = Decimal(comparison_value)
        except InvalidOperation:
            return None
        if baseline == 0:
            return None if comparison == 0 else "100"
        change = ((comparison - baseline) / baseline) * Decimal(100)
        return format(change.quantize(Decimal("0.01")), "f")

    @staticmethod
    def filter_metrics(
        metrics: tuple[MetricValueRecord, ...],
        metric_codes: frozenset[str],
    ) -> tuple[MetricValueRecord, ...]:
        """Filter metrics to requested codes when a filter is provided."""

        if not metric_codes:
            return metrics
        return tuple(metric for metric in metrics if metric.code in metric_codes)
