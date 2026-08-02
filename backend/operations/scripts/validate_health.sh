#!/usr/bin/env bash
# Validate API health endpoints against a running instance.
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
BASE_URL="${BASE_URL%/}"

echo "Validating health probes at ${BASE_URL}"

check() {
  local path="$1"
  local label="$2"
  local code
  code="$(curl --silent --output /dev/null --write-out '%{http_code}' --max-time 10 "${BASE_URL}${path}")"
  if [[ "${code}" != "200" ]]; then
    echo "FAIL ${label}: expected 200, got ${code} (${BASE_URL}${path})" >&2
    exit 1
  fi
  echo "OK   ${label} (${path})"
}

check "/health" "informational"
check "/live" "liveness"
check "/ready" "readiness"

echo "All health probes passed."
