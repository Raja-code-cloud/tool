# Prometheus

`PrometheusASGIApp` exposes one injected registry in the Prometheus text format. It is an ASGI app,
not a business route; process composition decides whether and where to mount it. Protect the
listener with network policy or platform authentication and do not expose it publicly.

Scrape intervals of 15–60 seconds are typical. Scraping should have a short timeout and `no-store`
is returned. Use a separate registry per test and per logical exporter. Multiprocess deployment
requires the Prometheus client's multiprocess directory and collector to be configured by the
runtime platform; do not combine per-process registries accidentally.

Prefer histogram rates and quantiles computed in PromQL. Alert on sustained rates and SLO burn,
not individual samples.
