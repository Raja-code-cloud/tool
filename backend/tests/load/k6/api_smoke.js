/**
 * k6 smoke load test for Cloud Content Hub API.
 *
 * Run:
 *   k6 run tests/load/k6/api_smoke.js
 *
 * With auth:
 *   k6 run -e CCH_BASE_URL=http://localhost:8000 \
 *          -e CCH_PERF_TOKEN=<token> \
 *          -e CCH_PERF_WORKSPACE=01900000-0000-7000-8000-000000000001 \
 *          tests/load/k6/api_smoke.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

const baseUrl = __ENV.CCH_BASE_URL || 'http://localhost:8000';
const token = __ENV.CCH_PERF_TOKEN || '';
const workspace =
  __ENV.CCH_PERF_WORKSPACE || '01900000-0000-7000-8000-000000000001';

const crudLatency = new Trend('cch_crud_latency_ms', true);
const errorRate = new Rate('cch_errors');

export const options = {
  vus: 1,
  duration: '30s',
  thresholds: {
    cch_crud_latency_ms: ['p(95)<300'],
    cch_errors: ['rate<0.01'],
    http_req_failed: ['rate<0.01'],
  },
};

function headers() {
  const h = {
    'X-Workspace-ID': workspace,
    'X-Correlation-ID': `k6-${__VU}-${__ITER}`,
  };
  if (token) {
    h['Authorization'] = `Bearer ${token}`;
  }
  return h;
}

export default function () {
  const health = http.get(`${baseUrl}/health`);
  check(health, { 'health 200': (r) => r.status === 200 });
  errorRate.add(health.status !== 200);

  const live = http.get(`${baseUrl}/live`);
  check(live, { 'live 200': (r) => r.status === 200 });

  if (token) {
    const assets = http.get(`${baseUrl}/api/v1/assets?limit=25`, { headers: headers() });
    crudLatency.add(assets.timings.duration);
    check(assets, { 'assets 200': (r) => r.status === 200 });
    errorRate.add(assets.status !== 200);

    const content = http.get(`${baseUrl}/api/v1/content?limit=25`, { headers: headers() });
    crudLatency.add(content.timings.duration);
    check(content, { 'content 200': (r) => r.status === 200 });
    errorRate.add(content.status !== 200);
  }

  sleep(0.5);
}
