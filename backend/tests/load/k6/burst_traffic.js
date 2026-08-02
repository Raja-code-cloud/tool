/**
 * k6 burst traffic scenario simulating scheduler/worker activity spikes.
 *
 * Run:
 *   k6 run tests/load/k6/burst_traffic.js
 */
import { check, sleep } from "k6";
import http from "k6/http";
import { Counter, Trend } from "k6/metrics";

const baseUrl = __ENV.CCH_BASE_URL || "http://localhost:8000";
const token = __ENV.CCH_PERF_TOKEN || "";
const workspace = __ENV.CCH_PERF_WORKSPACE || "01900000-0000-7000-8000-000000000001";

const burstRequests = new Counter("cch_burst_requests");
const burstLatency = new Trend("cch_burst_latency_ms", true);

export const options = {
  scenarios: {
    burst: {
      executor: "ramping-arrival-rate",
      startRate: 5,
      timeUnit: "1s",
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { duration: "10s", target: 5 },
        { duration: "10s", target: 100 },
        { duration: "20s", target: 100 },
        { duration: "10s", target: 5 },
      ],
    },
  },
  thresholds: {
    cch_burst_latency_ms: ["p(99)<2000"],
    http_req_failed: ["rate<0.10"],
  },
};

function headers() {
  const h = {
    "X-Workspace-ID": workspace,
    "X-Correlation-ID": `burst-${__VU}-${__ITER}`,
  };
  if (token) {
    h["Authorization"] = `Bearer ${token}`;
  }
  return h;
}

export default function () {
  burstRequests.add(1);

  const targets = token
    ? [
        "/api/v1/admin/jobs?limit=50",
        "/api/v1/admin/queues",
        "/api/v1/schedule?limit=50",
        "/api/v1/publish/history?limit=50",
      ]
    : ["/health", "/live", "/ready"];

  const path = targets[__ITER % targets.length];
  const response = http.get(`${baseUrl}${path}`, { headers: headers() });
  burstLatency.add(response.timings.duration);
  check(response, { reachable: (r) => r.status > 0 });
  sleep(0.05);
}
