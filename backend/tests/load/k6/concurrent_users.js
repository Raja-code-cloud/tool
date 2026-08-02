/**
 * k6 concurrent user load test (10 / 100 VU stages).
 *
 * Run:
 *   k6 run tests/load/k6/concurrent_users.js
 */
import { check, sleep } from "k6";
import http from "k6/http";
import { Rate, Trend } from "k6/metrics";

const baseUrl = __ENV.CCH_BASE_URL || "http://localhost:8000";
const token = __ENV.CCH_PERF_TOKEN || "";
const workspace = __ENV.CCH_PERF_WORKSPACE || "01900000-0000-7000-8000-000000000001";

const apiLatency = new Trend("cch_api_latency_ms", true);
const errorRate = new Rate("cch_errors");

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 10 },
    { duration: "30s", target: 100 },
    { duration: "2m", target: 100 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    cch_api_latency_ms: ["p(95)<500"],
    cch_errors: ["rate<0.05"],
  },
};

function headers() {
  const h = {
    "X-Workspace-ID": workspace,
    "X-Correlation-ID": `k6-${__VU}-${__ITER}`,
  };
  if (token) {
    h["Authorization"] = `Bearer ${token}`;
  }
  return h;
}

const endpoints = [
  "/api/v1/assets?limit=25",
  "/api/v1/assets/search?q=launch&limit=25",
  "/api/v1/content?limit=25",
  "/api/v1/analytics/dashboard",
  "/api/v1/notifications?limit=25",
];

export default function () {
  http.get(`${baseUrl}/health`);

  if (!token) {
    sleep(1);
    return;
  }

  const path = endpoints[__ITER % endpoints.length];
  const response = http.get(`${baseUrl}${path}`, { headers: headers() });
  apiLatency.add(response.timings.duration);
  check(response, { "status 2xx": (r) => r.status >= 200 && r.status < 300 });
  errorRate.add(response.status < 200 || response.status >= 300);
  sleep(Math.random() * 0.8 + 0.2);
}
